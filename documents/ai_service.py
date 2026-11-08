# documents/ai_service.py
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from django.conf import settings
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Multi-Model Registry with complete Mistral, OpenAI, Groq versions
SUPPORTED_MODELS = [
    # ── MISTRAL AI MODELS (Direct Mistral API / OpenRouter) ──
    {
        'id': 'mistral-tiny',
        'name': 'Mistral 7B (Tiny)',
        'provider': 'mistral',
        'badge': 'Fast & Light',
        'category': 'Mistral AI',
        'description': 'Superfast standard Mistral conversational model'
    },
    {
        'id': 'mistral-small-latest',
        'name': 'Mistral Small (24B Latest)',
        'provider': 'mistral',
        'badge': 'Balanced SOTA',
        'category': 'Mistral AI',
        'description': 'Latest 2025 small flagship by Mistral AI'
    },
    {
        'id': 'mistral-medium-latest',
        'name': 'Mistral Medium',
        'provider': 'mistral',
        'badge': 'High Reasoning',
        'category': 'Mistral AI',
        'description': 'Superior multi-lingual reasoning and synthesis'
    },
    {
        'id': 'mistral-large-latest',
        'name': 'Mistral Large 2 (Flagship)',
        'provider': 'mistral',
        'badge': 'Pro Flagship',
        'category': 'Mistral AI',
        'description': 'Top 128k context reasoning rivaling GPT-4o'
    },
    {
        'id': 'codestral-latest',
        'name': 'Codestral (Mistral Code)',
        'provider': 'mistral',
        'badge': 'Code & Specs',
        'category': 'Mistral AI',
        'description': 'Trained specifically for structured docs & syntax'
    },
    {
        'id': 'mistralai/mistral-7b-instruct:free',
        'name': 'Mistral 7B (OpenRouter Free)',
        'provider': 'openrouter',
        'badge': '100% Free',
        'category': 'Mistral AI',
        'description': 'Free open-source tier via OpenRouter'
    },

    # ── OPENAI GPT MODELS ──
    {
        'id': 'gpt-4o-mini',
        'name': 'GPT-4o Mini',
        'provider': 'openai',
        'badge': 'Fast & Smart',
        'category': 'OpenAI',
        'description': 'OpenAI high-speed multimodal intelligence'
    },
    {
        'id': 'gpt-4o',
        'name': 'GPT-4o (Omni)',
        'provider': 'openai',
        'badge': 'SOTA Reasoning',
        'category': 'OpenAI',
        'description': 'Flagship multimodal reasoning engine'
    },
    {
        'id': 'gpt-3.5-turbo',
        'name': 'GPT-3.5 Turbo',
        'provider': 'openai',
        'badge': 'Legacy Fast',
        'category': 'OpenAI',
        'description': 'Traditional fast chat model'
    },

    # ── GOOGLE GEMINI MODELS ──
    {
        'id': 'google/gemini-2.0-flash-exp:free',
        'name': 'Gemini 2.0 Flash (Free)',
        'provider': 'openrouter',
        'badge': 'Free Next-Gen',
        'category': 'Google Gemini',
        'description': 'Google next-gen high-speed multimodal model'
    },

    # ── META LLAMA & GROQ ──
    {
        'id': 'meta-llama/llama-3.3-70b-instruct:free',
        'name': 'Llama 3.3 70B (Free)',
        'provider': 'openrouter',
        'badge': 'Free 70B',
        'category': 'Meta Llama',
        'description': 'Top benchmark open-weights intelligence'
    },
    {
        'id': 'llama-3.3-70b-versatile',
        'name': 'Groq Llama 3.3 70B',
        'provider': 'groq',
        'badge': 'Ultra-Speed',
        'category': 'Groq',
        'description': 'Sub-second real-time streaming inference'
    }
]


def resolve_credentials(user=None, model_id=None):
    selected_model = model_id or (getattr(user, 'preferred_model', None) if user else None) or "mistralai/mistral-7b-instruct:free"

    # Identify provider
    api_key = None
    base_url = None
    provider = "openrouter"

    # Mistral Direct Models
    if selected_model.startswith("mistral-") or selected_model.startswith("codestral-"):
        provider = "mistral"
        api_key = (getattr(user, 'mistral_api_key', None) if user else None) or os.getenv('MISTRAL_API_KEY')
        base_url = "https://api.mistral.ai/v1"
        # If user has no direct Mistral key but has OpenRouter key, route through openrouter
        if not api_key:
            openrouter_key = (getattr(user, 'openrouter_api_key', None) if user else None) or os.getenv('OPENROUTER_API_KEY')
            if openrouter_key:
                api_key = openrouter_key
                base_url = "https://openrouter.ai/api/v1"
                selected_model = f"mistralai/{selected_model}"

    elif selected_model.startswith("gpt-"):
        provider = "openai"
        api_key = (getattr(user, 'openai_api_key', None) if user else None) or os.getenv('OPENAI_API_KEY')
        base_url = None

    elif selected_model.startswith("llama-3.3-70b-versatile") or "groq" in selected_model:
        provider = "groq"
        api_key = (getattr(user, 'groq_api_key', None) if user else None) or os.getenv('GROQ_API_KEY')
        base_url = "https://api.groq.com/openai/v1"

    else:  # OpenRouter free tiers (mistralai/*, meta-llama/*, google/*)
        provider = "openrouter"
        api_key = (getattr(user, 'openrouter_api_key', None) if user else None) or os.getenv('OPENROUTER_API_KEY')
        base_url = "https://openrouter.ai/api/v1"

    if api_key and (api_key.startswith('your-') or 'dummy' in api_key):
        api_key = None

    return {
        'model': selected_model,
        'provider': provider,
        'api_key': api_key,
        'base_url': base_url
    }


def get_llm(user=None, model_id=None):
    cred = resolve_credentials(user, model_id)
    key = cred['api_key'] or "dummy-key"

    kwargs = {
        'model': cred['model'],
        'api_key': key,
        'temperature': 0.4,
        'max_tokens': 1500
    }
    if cred['base_url']:
        kwargs['base_url'] = cred['base_url']

    return ChatOpenAI(**kwargs)


def get_embeddings(user=None):
    cred = resolve_credentials(user)
    key = cred['api_key'] or "dummy-key"
    base_url = cred['base_url']

    kwargs = {
        'model': "text-embedding-ada-002",
        'api_key': key
    }
    if base_url:
        kwargs['base_url'] = base_url

    return OpenAIEmbeddings(**kwargs)


def extract_fallback_summary_and_keypoints(file_path: str):
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        full_text = " ".join([p.page_content for p in pages if p.page_content])
        cleaned_text = re.sub(r'\s+', ' ', full_text).strip()

        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned_text) if len(s.strip()) > 30]

        summary = " ".join(sentences[:3]) if sentences else "PDF document uploaded successfully."
        key_points = sentences[1:6] if len(sentences) >= 6 else (sentences[:5] if sentences else ["Document processed successfully."])

        return summary, key_points
    except Exception as e:
        return f"Summary unavailable: {str(e)}", ["Document text extraction completed."]


def process_document(document_id: int, file_path: str, user=None) -> dict:
    try:
        loader    = PyPDFLoader(file_path)
        documents = loader.load()
        pages     = len(documents)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size    = 500,
            chunk_overlap = 50
        )
        chunks = splitter.split_documents(documents)

        collection_name = f"doc_{document_id}"
        chroma_path     = os.path.join(
            settings.CHROMA_DB_PATH,
            collection_name
        )

        cred = resolve_credentials(user)
        if cred['api_key']:
            try:
                Chroma.from_documents(
                    documents         = chunks,
                    embedding         = get_embeddings(user),
                    persist_directory = chroma_path
                )
            except Exception:
                pass

        return {
            'success': True,
            'pages':   pages,
            'chunks':  len(chunks)
        }

    except Exception as e:
        return {
            'success': False,
            'error':   str(e)
        }


def get_vectorstore(document_id: int, user=None):
    collection_name = f"doc_{document_id}"
    chroma_path     = os.path.join(
        settings.CHROMA_DB_PATH,
        collection_name
    )

    return Chroma(
        persist_directory  = chroma_path,
        embedding_function = get_embeddings(user)
    )


# ── General Direct Chat (Without Document - Pure ChatGPT Experience & Vision) ──
def general_chat(question: str, history: list = None, user=None, model_id=None, image_data: str = None) -> dict:
    cred = resolve_credentials(user, model_id)

    if not cred['api_key']:
        model_name = cred['model']
        image_notice = "\n\n📷 *Image captured/uploaded!*" if image_data else ""
        answer = f"Hello! Main **PolyMind AI** hoon. Aapne model select kiya hai: `{model_name}`.{image_notice}\n\nLive AI streaming aur vision responses ke liye **Settings** page par apni `{cred['provider'].upper()}` API Key enter karein (Mistral, OpenRouter, OpenAI, ya Groq).\n\nAap text aur voice input ke sath direct conversation kar sakte hain!"
        return {
            'success': True,
            'answer': answer,
            'sources': [],
            'model_used': cred['model']
        }

    try:
        llm = get_llm(user, model_id)
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

        messages = [
            SystemMessage(content="You are PolyMind AI, a brilliant and versatile AI assistant. Answer user questions clearly and thoughtfully. If an image is provided, thoroughly analyze and describe or answer questions about the captured image. Format code inside markdown blocks.")
        ]

        if history:
            for item in history[-6:]:
                role = item.get('role')
                content = item.get('content', '')
                if role == 'user':
                    messages.append(HumanMessage(content=content))
                elif role == 'assistant':
                    messages.append(AIMessage(content=content))

        # Build message with image if present
        if image_data:
            content_payload = []
            user_text = question.strip() if question else "Analyze this captured image and describe what you see in detail."
            content_payload.append({"type": "text", "text": user_text})
            content_payload.append({
                "type": "image_url",
                "image_url": {"url": image_data}
            })
            messages.append(HumanMessage(content=content_payload))
        else:
            messages.append(HumanMessage(content=question))

        ai_response = llm.invoke(messages)
        content_text = ai_response.content if hasattr(ai_response, 'content') else str(ai_response)

        return {
            'success': True,
            'answer': content_text,
            'sources': [],
            'model_used': cred['model']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'model_used': cred['model']
        }


# ── Ask Question (With Document or Pure Chat / Vision) ──
def ask_question(document_id=None, question=str, user=None, model_id=None, image_data: str = None) -> dict:
    if not document_id:
        return general_chat(question=question, user=user, model_id=model_id, image_data=image_data)

    from .models import Document
    doc_obj = Document.objects.filter(id=document_id).first()
    if not doc_obj:
        return general_chat(question=question, user=user, model_id=model_id, image_data=image_data)

    cred = resolve_credentials(user, model_id)

    if image_data:
        # If user attached an image, pass to vision-capable multimodal
        return general_chat(question=question, user=user, model_id=model_id, image_data=image_data)

    if not cred['api_key']:
        sources = []
        if doc_obj and doc_obj.file and os.path.exists(doc_obj.file.path):
            try:
                loader = PyPDFLoader(doc_obj.file.path)
                pages = loader.load()
                keywords = [w.lower() for w in re.findall(r'\w+', question) if len(w) > 3]
                best_page = 1
                best_match_count = 0
                snippet = ""

                for p_idx, page in enumerate(pages):
                    text_lower = page.page_content.lower()
                    matches = sum(1 for kw in keywords if kw in text_lower)
                    if matches > best_match_count:
                        best_match_count = matches
                        best_page = p_idx + 1
                        snippet = page.page_content[:300]

                if snippet:
                    sources = [{'page': best_page, 'content': snippet}]
                    answer = f"Relevant section from Document (Page {best_page}):\n\n\"{snippet}...\"\n\n💡 Tip: Settings page par apni {cred['provider'].upper()} API Key save karke live answers paayein using {cred['model']}."
                else:
                    first_p = pages[0].page_content[:300] if pages else ""
                    sources = [{'page': 1, 'content': first_p}]
                    answer = f"Context: {doc_obj.summary or first_p}\n\n💡 Settings page par apni API key daalein for direct generative chat."
            except Exception:
                answer = "Document loaded. Please configure an API Key in Settings to enable generative QA."
        else:
            answer = "Document context loaded. Please add API Key in Settings."

        return {
            'success': True,
            'answer': answer,
            'sources': sources,
            'model_used': cred['model']
        }

    try:
        vectorstore = get_vectorstore(document_id, user)

        prompt = PromptTemplate(
            template = """
            Neeche diye gaye context aur question ke basis par clean, precise answer do.
            Agar context me information na ho, to general helpful guidance do.

            Context: {context}
            Question: {question}

            Answer:
            """,
            input_variables = ["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm                     = get_llm(user, model_id),
            retriever               = vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs       = {"prompt": prompt},
            return_source_documents = True
        )

        result  = qa_chain.invoke({"query": question})
        sources = [
            {
                'content': doc.page_content[:200],
                'page':    doc.metadata.get('page', 0) + 1
            }
            for doc in result.get('source_documents', [])
        ]

        return {
            'success': True,
            'answer':  result.get('result', ''),
            'sources': sources,
            'model_used': cred['model']
        }

    except Exception as e:
        fallback_res = general_chat(question, user=user, model_id=model_id)
        if fallback_res.get('success'):
            return fallback_res
        return {
            'success': False,
            'error':   str(e),
            'model_used': cred['model']
        }


def generate_summary(document_id: int, user=None, model_id=None) -> str:
    from .models import Document
    doc_obj = Document.objects.filter(id=document_id).first()
    cred = resolve_credentials(user, model_id)

    if not cred['api_key']:
        if doc_obj and doc_obj.file and os.path.exists(doc_obj.file.path):
            summary, _ = extract_fallback_summary_and_keypoints(doc_obj.file.path)
            return summary
        return "Smart document summary generated."

    try:
        vectorstore = get_vectorstore(document_id, user)

        prompt = PromptTemplate(
            template = """
            Context ke aadhar par document ka concise executive summary likhein:
            1. Overview
            2. Main topics
            3. Key takeaways

            Context: {context}
            Question: {question}

            Summary:
            """,
            input_variables = ["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm               = get_llm(user, model_id),
            retriever         = vectorstore.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs = {"prompt": prompt}
        )

        result = qa_chain.invoke({"query": "Document ka complete executive summary do"})
        return result['result']

    except Exception as e:
        if doc_obj and doc_obj.file and os.path.exists(doc_obj.file.path):
            summary, _ = extract_fallback_summary_and_keypoints(doc_obj.file.path)
            return summary
        return f"Summary note: {str(e)}"


def extract_key_points(document_id: int, user=None, model_id=None) -> list:
    from .models import Document
    doc_obj = Document.objects.filter(id=document_id).first()
    cred = resolve_credentials(user, model_id)

    if not cred['api_key']:
        if doc_obj and doc_obj.file and os.path.exists(doc_obj.file.path):
            _, key_points = extract_fallback_summary_and_keypoints(doc_obj.file.path)
            return key_points
        return ["Document uploaded and processed successfully."]

    try:
        vectorstore = get_vectorstore(document_id, user)

        prompt = PromptTemplate(
            template = """
            Context me se 5-7 mahatvapurna key bullet points nikalo.
            Format:
            - Point 1
            - Point 2
            - Point 3

            Context: {context}
            Question: {question}

            Key Points:
            """,
            input_variables = ["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm               = get_llm(user, model_id),
            retriever         = vectorstore.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs = {"prompt": prompt}
        )

        result = qa_chain.invoke({"query": "Document ke main key points kya hain?"})
        points_text = result['result']
        points = [
            p.strip().lstrip('-•*').strip()
            for p in points_text.split('\n')
            if p.strip() and p.strip() not in ('-', '•', '*')
        ]
        return points if points else ["Key points extracted."]

    except Exception as e:
        if doc_obj and doc_obj.file and os.path.exists(doc_obj.file.path):
            _, key_points = extract_fallback_summary_and_keypoints(doc_obj.file.path)
            return key_points
        return [f"Extracted info: {str(e)}"]
