# documents/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Document, ChatSession, ChatMessage
from .serializers import (
    DocumentListSerializer,
    DocumentDetailSerializer,
    DocumentUploadSerializer,
    ChatSessionSerializer,
    ChatSessionCreateSerializer,
    AskQuestionSerializer,
    ChatMessageSerializer
)
from .ai_service import (
    process_document,
    ask_question,
    generate_summary,
    extract_key_points,
    SUPPORTED_MODELS
)
import os


# ── 0. Supported Models List API ──────
class SupportedModelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'models': SUPPORTED_MODELS,
            'current_user_model': getattr(request.user, 'preferred_model', 'mistralai/mistral-7b-instruct:free')
        })


# ── 1. Document Upload (Also supports Drag & Drop direct ingestion) ──
class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        # Auto-fill title if user dropped file without explicit title
        data = request.data.copy()
        if not data.get('title') and 'file' in request.FILES:
            file_name = request.FILES['file'].name
            data['title'] = os.path.splitext(file_name)[0]

        serializer = DocumentUploadSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        document           = serializer.save(user=request.user)
        document.file_size = document.file.size
        document.status    = 'processing'
        document.save()

        file_path = document.file.path
        result    = process_document(document.id, file_path, user=request.user)

        if result['success']:
            document.pages  = result['pages']
            document.status = 'ready'
            document.summary    = generate_summary(document.id, user=request.user)
            document.key_points = extract_key_points(document.id, user=request.user)
            document.save()

            return Response(DocumentDetailSerializer(document).data, status=status.HTTP_201_CREATED)
        else:
            document.status = 'failed'
            document.save()
            return Response({'error': f"Processing failed: {result['error']}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── 2. Document List ──────────────────
class DocumentListView(generics.ListAPIView):
    serializer_class   = DocumentListSerializer
    permission_classes = [IsAuthenticated]
    search_fields      = ['title', 'tags']
    ordering_fields    = ['created_at', 'title']

    def get_queryset(self):
        queryset = Document.objects.filter(user=self.request.user)

        is_favourite = self.request.query_params.get('is_favourite')
        if is_favourite == 'true':
            queryset = queryset.filter(is_favourite=True)

        doc_status = self.request.query_params.get('status')
        if doc_status:
            queryset = queryset.filter(status=doc_status)

        return queryset


# ── 3. Document Detail ────────────────
class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Document, pk=pk, user=user)

    def get(self, request, pk):
        document   = self.get_object(pk, request.user)
        serializer = DocumentDetailSerializer(document)
        return Response(serializer.data)

    def patch(self, request, pk):
        document   = self.get_object(pk, request.user)
        serializer = DocumentDetailSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        document = self.get_object(pk, request.user)
        try:
            chroma_path = os.path.join(settings.CHROMA_DB_PATH, f"doc_{document.id}")
            if os.path.exists(chroma_path):
                import shutil
                shutil.rmtree(chroma_path)
        except Exception:
            pass

        document.delete()
        return Response({'message': 'Document deleted!'}, status=status.HTTP_204_NO_CONTENT)


# ── 4. Toggle Favourite ───────────────
class ToggleFavouriteView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        document = get_object_or_404(Document, pk=pk, user=request.user)
        document.is_favourite = not document.is_favourite
        document.save()
        return Response({'message': 'Updated!', 'is_favourite': document.is_favourite})


# ── 5. Unified Ask Question (Doc RAG or General ChatGPT-style) ──
class AskQuestionView(APIView):
    """
    POST /api/documents/ask/ or /api/documents/<id>/ask/
    Works both with and without document!
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        serializer = AskQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question     = serializer.validated_data.get('question', '').strip()
        image_data   = serializer.validated_data.get('image', '').strip()
        session_id   = serializer.validated_data.get('session_id')
        chosen_model = serializer.validated_data.get('model') or request.user.preferred_model
        doc_id       = pk or serializer.validated_data.get('document_id')

        if not question and not image_data:
            return Response({'error': 'Please provide either a question or an image.'}, status=status.HTTP_400_BAD_REQUEST)

        document = None
        if doc_id:
            document = get_object_or_404(Document, pk=doc_id, user=request.user)

        # Chat session get or create
        if session_id:
            session = get_object_or_404(ChatSession, pk=session_id)
        else:
            session_title = (question[:50] if question else "Image Query")
            session = ChatSession.objects.create(
                document = document,
                user     = request.user if not document else None,
                title    = session_title
            )

        # Call multi-model QA with optional image support
        result = ask_question(
            document_id = document.id if document else None,
            question    = question,
            user        = request.user,
            model_id    = chosen_model,
            image_data  = image_data or None
        )

        if not result.get('success', False):
            return Response({'error': result.get('error', 'Inference failed.')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save user message
        ChatMessage.objects.create(
            session = session,
            role    = 'user',
            content = question if question else "[Captured Image]",
            image   = image_data if image_data else None
        )

        # Save assistant message
        ChatMessage.objects.create(
            session    = session,
            role       = 'assistant',
            content    = result['answer'],
            sources    = result.get('sources', []),
            model_name = result.get('model_used', chosen_model)
        )

        session.save()

        return Response({
            'session_id': session.id,
            'question':   question,
            'image':      image_data,
            'answer':     result['answer'],
            'sources':    result.get('sources', []),
            'model_used': result.get('model_used', chosen_model)
        })


# ── 6. Get Summary ────────────────────
class DocumentSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk, user=request.user)
        force_refresh = request.query_params.get('refresh') == 'true'

        if document.summary and not force_refresh:
            return Response({'summary': document.summary, 'key_points': document.key_points})

        summary    = generate_summary(document.id, user=request.user)
        key_points = extract_key_points(document.id, user=request.user)

        document.summary    = summary
        document.key_points = key_points
        document.save()

        return Response({'summary': summary, 'key_points': key_points})


# ── 7. Chat Sessions (General + Document Sessions) ──
class ChatSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            document = get_object_or_404(Document, pk=pk, user=request.user)
            sessions = document.chats.all()
        else:
            # All user general chats
            sessions = ChatSession.objects.filter(user=request.user, document__isnull=True)

        return Response(ChatSessionSerializer(sessions, many=True).data)

    def post(self, request, pk=None):
        document = get_object_or_404(Document, pk=pk, user=request.user) if pk else None
        serializer = ChatSessionCreateSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save(document=document, user=request.user if not document else None)
            return Response(ChatSessionSerializer(session).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── 8. Chat Session Detail ────────────
class ChatSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, chat_id=None):
        cid = chat_id or pk
        session = get_object_or_404(ChatSession, pk=cid)
        return Response(ChatSessionSerializer(session).data)

    def delete(self, request, pk=None, chat_id=None):
        cid = chat_id or pk
        session = get_object_or_404(ChatSession, pk=cid)
        session.delete()
        return Response({'message': 'Chat deleted!'}, status=status.HTTP_204_NO_CONTENT)


# ── 9. Dashboard Stats ────────────────
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user      = request.user
        documents = Document.objects.filter(user=user)

        total_questions = ChatMessage.objects.filter(
            session__user=user, role='user'
        ).count() + ChatMessage.objects.filter(
            session__document__user=user, role='user'
        ).count()

        recent_docs = DocumentListSerializer(documents[:5], many=True).data

        return Response({
            'total_documents': documents.count(),
            'ready_documents': documents.filter(status='ready').count(),
            'favourite_count': documents.filter(is_favourite=True).count(),
            'total_questions': total_questions,
            'recent_documents': recent_docs,
            'preferred_model': getattr(user, 'preferred_model', 'mistralai/mistral-7b-instruct:free')
        })
