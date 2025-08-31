# AI-Powered Legal Document Analysis System
import os
import streamlit as st
import tempfile
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.embedder.openai import OpenAIEmbedder
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.chroma import ChromaDb
from agno.document.chunking.document import DocumentChunking

# Configure Streamlit application
st.set_page_config(
    page_title="AI Legal Document Analyzer", 
    page_icon="⚖️", 
    layout="wide"
)

# Application header with enhanced styling
st.markdown(
    "<h1 style='text-align: center; color: #3e8e41;'>🤖 AI Legal Document Analyzer</h1>", 
    unsafe_allow_html=True
)

# Application description with improved messaging
st.markdown("""
    <div style='text-align: center; font-size: 18px; color: #4B0082;'>
        Submit your legal documents and harness the capabilities of <b>AI Legal Advisor</b>, <b>AI Contract Examiner</b>, 
        <b>AI Risk Assessor</b>, and <b>AI Analysis Coordinator</b> for thorough legal examination. 
        Engage with the platform using personalized inquiries to facilitate enhanced teamwork and comprehensive document review.
    </div>
""", unsafe_allow_html=True)

# Initialize application state
if "vector_database" not in st.session_state:
    st.session_state.vector_database = ChromaDb(
        collection="legal_docs", 
        path="tmp/chromadb", 
        persistent_client=True, 
        embedder=OpenAIEmbedder()
    )

if "document_knowledge_base" not in st.session_state:
    st.session_state.document_knowledge_base = None

if "processed_documents" not in st.session_state:
    st.session_state.processed_documents = set()

# Sidebar configuration and document management
with st.sidebar:
    # Configuration section
    st.header("⚙️ System Configuration")

    # API key input with enhanced security
    api_key_input = st.sidebar.text_input(
        label="Enter your OpenAI API Key:",
        type="password",
        help="Your personal OpenAI API key for accessing the service."
    )

    # Set API key in environment
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input
        st.success("✅ OpenAI API key configured successfully!")

    else:
        st.warning("⚠️ Please enter your API key to proceed.")

    # Document processing parameters
    chunk_size_parameter = st.sidebar.number_input(
        "Document Chunk Size", 
        min_value=1, 
        max_value=5000, 
        value=1000
    )
    overlap_parameter = st.sidebar.number_input(
        "Chunk Overlap", 
        min_value=1, 
        max_value=1000, 
        value=200
    )

    # Document upload section
    st.header("📄 Document Management")

    uploaded_document = st.file_uploader(
        "Upload a Legal Document (PDF)", 
        type=["pdf"]
    )
    
    if uploaded_document:
        if uploaded_document.name not in st.session_state.processed_documents:
            with st.spinner("Processing document..."):
                try:
                    # Create temporary file for processing
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_file.write(uploaded_document.getvalue())
                        temp_file_path = temp_file.name
                    
                    # Initialize knowledge base with uploaded document
                    st.session_state.document_knowledge_base = PDFKnowledgeBase(
                        path=temp_file_path,
                        vector_db=st.session_state.vector_database,
                        reader=PDFReader(),
                        chunking_strategy=DocumentChunking(
                            chunk_size=chunk_size_parameter, 
                            overlap=overlap_parameter
                        )
                    )

                    # Load document into knowledge base
                    st.session_state.document_knowledge_base.load(recreate=True, upsert=True)
                    
                    # Verify knowledge base functionality
                    try:
                        verification_query = "test"
                        verification_results = st.session_state.document_knowledge_base.search(verification_query)
                        if verification_results:
                            st.success(f"✅ Knowledge base verified with {len(verification_results)} searchable chunks")
                        else:
                            st.warning("⚠️ Knowledge base created but no searchable content found")
                    except Exception as verification_error:
                        st.error(f"❌ Knowledge base verification failed: {verification_error}")
                    
                    st.session_state.processed_documents.add(uploaded_document.name)

                    st.success("✅ Document processed and stored in knowledge base!")
                    
                    # Display document information
                    st.info(f"📊 Document Details: {uploaded_document.name} ({uploaded_document.size} bytes)")
                    st.info(f"🔍 Knowledge Base Status: Active with {len(st.session_state.processed_documents)} document(s)")
                    
                    # Knowledge base testing interface
                    test_column_1, test_column_2 = st.columns(2)
                    
                    with test_column_1:
                        if st.button("🔍 Test Knowledge Base Content"):
                            try:
                                test_search_results = st.session_state.document_knowledge_base.search("employment contract")
                                st.info(f"🔍 Search method returned: {type(test_search_results)}")
                                st.info(f"🔍 Search result length: {len(test_search_results) if hasattr(test_search_results, '__len__') else 'No length attribute'}")
                                
                                if test_search_results:
                                    st.success(f"✅ Knowledge base search successful! Found results")
                                    # Display search results
                                    if hasattr(test_search_results, '__getitem__'):
                                        for result_index in range(min(3, len(test_search_results))):
                                            result_content = str(test_search_results[result_index])[:200] + "..." if len(str(test_search_results[result_index])) > 200 else str(test_search_results[result_index])
                                            st.text_area(f"Chunk {result_index+1}:", result_content, height=80, disabled=True)
                                    else:
                                        st.text_area("Result:", str(test_search_results)[:500] + "...", height=100, disabled=True)
                                else:
                                    st.warning("⚠️ No search results found in knowledge base")
                            except Exception as search_error:
                                st.error(f"❌ Knowledge base search error: {search_error}")
                                st.error(f"Error type: {type(search_error)}")
                                st.error(f"Error details: {str(search_error)}")
                    
                    with test_column_2:
                        if st.button("🔍 Test Knowledge Base Methods"):
                            try:
                                # Display available methods
                                available_methods = [method for method in dir(st.session_state.document_knowledge_base) if not method.startswith('_')]
                                st.info(f"Available methods: {', '.join(available_methods[:10])}")
                                
                                # Get document count
                                if hasattr(st.session_state.document_knowledge_base, 'get_documents'):
                                    document_list = st.session_state.document_knowledge_base.get_documents()
                                    st.info(f"Documents in knowledge base: {len(document_list) if document_list else 0}")
                            except Exception as method_test_error:
                                st.error(f"Method test error: {method_test_error}")
                    
                    # Document content preview
                    try:
                        import pypdf
                        with open(temp_file_path, 'rb') as file:
                            pdf_reader = pypdf.PdfReader(file)
                            page_count = len(pdf_reader.pages)
                            st.info(f"📄 PDF Pages: {page_count}")
                            
                            # First page preview
                            if page_count > 0:
                                first_page_content = pdf_reader.pages[0]
                                text_preview = first_page_content.extract_text()[:200] + "..." if len(first_page_content.extract_text()) > 200 else first_page_content.extract_text()
                                st.text_area("📝 First Page Preview:", text_preview, height=100, disabled=True)
                    except Exception as preview_error:
                        st.warning(f"Could not preview PDF content: {preview_error}")

                except Exception as processing_error:
                    st.error(f"Error processing document: {processing_error}")
                    
# Function to initialize AI agents with current knowledge base
def initialize_ai_agents():
    if st.session_state.document_knowledge_base:
        # Verify knowledge base status
        try:
            knowledge_base_test = st.session_state.document_knowledge_base.search("test")
            st.info(f"🔍 Knowledge base search test: Found {len(knowledge_base_test) if knowledge_base_test else 0} results")
        except Exception as knowledge_base_error:
            st.error(f"❌ Knowledge base search failed: {knowledge_base_error}")
        
        # Initialize Legal Advisor agent
        legal_advisor_agent = Agent(
            name="LegalAdvisor",
            model=OpenAIChat(id="gpt-4o-mini"),
            knowledge=st.session_state.document_knowledge_base,
            search_knowledge=True,
            description="AI Legal Advisor - Discovers and references relevant legal cases, regulations, and precedents using comprehensive document data.",
            instructions=[
                "IMPORTANT: You have access to a knowledge base containing the uploaded legal document. Use search_knowledge=True to access this content.",
                "First, search the knowledge base for the document content using relevant keywords.",
                "Extract all available data from the knowledge base and search for legal cases, regulations, and citations.",
                "If needed, use DuckDuckGo for additional legal references.",
                "Always provide source references in your answers.",
                "If you cannot find content, explicitly state what you searched for and what was found."
            ],  
            tools=[DuckDuckGoTools()],
            show_tool_calls=True,
            markdown=True
        )

        # Initialize Contract Examiner agent
        contract_examiner_agent = Agent(
            name="ContractExaminer",
            model=OpenAIChat(id="gpt-4o-mini"),
            knowledge=st.session_state.document_knowledge_base,
            search_knowledge=True,
            description="AI Contract Examiner - Reviews contracts and identifies key clauses, risks, and obligations using comprehensive document data.",
            instructions=[
                "IMPORTANT: You have access to a knowledge base containing the uploaded legal document. Use search_knowledge=True to access this content.",
                "First, search the knowledge base for the document content using relevant keywords like 'contract', 'agreement', 'terms', 'clauses'.",
                "Extract all available data from the knowledge base and analyze the contract for key clauses, obligations, and potential ambiguities.",
                "Reference specific sections of the contract where possible.",
                "If you cannot find content, explicitly state what you searched for and what was found."
            ],
            show_tool_calls=True,
            markdown=True
        )

        # Initialize Risk Assessor agent
        risk_assessor_agent = Agent(
            name="RiskAssessor",
            model=OpenAIChat(id="gpt-4o-mini"),
            knowledge=st.session_state.document_knowledge_base,
            search_knowledge=True,
            description="AI Risk Assessor - Provides comprehensive risk assessment and strategic recommendations based on comprehensive contract data.",
            instructions=[
                "IMPORTANT: You have access to a knowledge base containing the uploaded legal document. Use search_knowledge=True to access this content.",
                "First, search the knowledge base for the document content using relevant keywords like 'risk', 'liability', 'obligation', 'compliance'.",
                "Using all data from the knowledge base, assess the contract for legal risks and opportunities.",
                "Provide actionable recommendations and ensure compliance with applicable laws.",
                "If you cannot find content, explicitly state what you searched for and what was found."
            ],
            show_tool_calls=True,
            markdown=True
        )

        # Initialize Analysis Coordinator agent
        analysis_coordinator_agent = Agent(
            name="AnalysisCoordinator",
            model=OpenAIChat(id="gpt-4o-mini"),
            description="AI Analysis Coordinator - Integrates responses from the Legal Advisor, Contract Examiner, and Risk Assessor into a comprehensive report.",
            instructions=[
                "Combine and summarize all insights provided by the Legal Advisor, Contract Examiner, and Risk Assessor. "
                "Ensure the final report includes references to all relevant sections from the document."
            ],
            show_tool_calls=True,
            markdown=True
        )

        return legal_advisor_agent, contract_examiner_agent, risk_assessor_agent, analysis_coordinator_agent
    return None, None, None, None

# Function to generate comprehensive team analysis
def generate_team_analysis(analysis_query):
    legal_advisor_agent, contract_examiner_agent, risk_assessor_agent, analysis_coordinator_agent = initialize_ai_agents()
    
    if not all([legal_advisor_agent, contract_examiner_agent, risk_assessor_agent, analysis_coordinator_agent]):
        return "Error: AI agents not properly initialized. Please ensure a document is uploaded and processed."
    
    # Execute agent analysis with focused queries
    legal_research_output = legal_advisor_agent.run(f"Research legal aspects of: {analysis_query}")
    contract_analysis_output = contract_examiner_agent.run(f"Analyze contract for: {analysis_query}")
    risk_assessment_output = risk_assessor_agent.run(f"Assess risks and strategy for: {analysis_query}")

    # Generate comprehensive report
    comprehensive_report = analysis_coordinator_agent.run(
        f"Create a concise legal analysis report covering:\n"
        f"1. Key findings from research\n"
        f"2. Contract analysis highlights\n" 
        f"3. Risk assessment summary\n"
        f"4. Strategic recommendations\n\n"
        f"Research: {str(legal_research_output)[:500]}...\n"
        f"Contract: {str(contract_analysis_output)[:500]}...\n"
        f"Strategy: {str(risk_assessment_output)[:500]}..."
    )
    return comprehensive_report

# Main analysis interface
if st.session_state.document_knowledge_base:
    st.header("🔍 Select Analysis Type")
    
    # Display knowledge base status
    st.success(f"✅ Knowledge Base Ready! {len(st.session_state.processed_documents)} document(s) loaded")
    
    # Show available documents
    if st.session_state.processed_documents:
        st.info(f"📚 Available Documents: {', '.join(st.session_state.processed_documents)}")
    
    # Debug information panel
    with st.expander("🔍 Debug: Knowledge Base Details"):
        try:
            # Test knowledge base search
            debug_search_results = st.session_state.document_knowledge_base.search("test")
            st.info(f"Search test results: {len(debug_search_results) if debug_search_results else 0}")
            
            # Display vector database information
            if hasattr(st.session_state.vector_database, 'get_collection'):
                database_collection = st.session_state.vector_database.get_collection()
                if database_collection:
                    collection_count = database_collection.count()
                    st.info(f"Vector DB collection count: {collection_count}")
                else:
                    st.warning("No collection found in vector database")
        except Exception as debug_error:
            st.error(f"Debug error: {debug_error}")
    
    # Analysis type selection
    analysis_type_selection = st.selectbox(
        "Choose Analysis Type:",
        ["Contract Review", "Legal Research", "Risk Assessment", "Compliance Check", "Custom Query"]
    )

    analysis_query_input = None
    if analysis_type_selection == "Custom Query":
        analysis_query_input = st.text_area("Enter your custom legal question:")
    else:
        predefined_analysis_queries = {
            "Contract Review": (
                "Analyze this document, contract, or agreement using all available data from the knowledge base. "
                "Identify key terms, obligations, and risks in detail."
            ),
            "Legal Research": (
                "Using all available data from the knowledge base, find relevant legal cases and precedents related to this document, contract, or agreement. "
                "Provide detailed references and sources."
            ),
            "Risk Assessment": (
                "Extract all data from the knowledge base and identify potential legal risks in this document, contract, or agreement. "
                "Detail specific risk areas and reference sections of the text."
            ),
            "Compliance Check": (
                "Evaluate this document, contract, or agreement for compliance with legal regulations using all available data from the knowledge base. "
                "Highlight any areas of concern and suggest corrective actions."
            )
        }
        analysis_query_input = predefined_analysis_queries[analysis_type_selection]

    if st.button("Analyze"):
        if not analysis_query_input:
            st.warning("Please enter a query.")
        else:
            with st.spinner("Analyzing..."):
                analysis_response = generate_team_analysis(analysis_query_input)

                # Display analysis results in organized tabs
                result_tabs = st.tabs(["Analysis", "Key Points", "Recommendations"])

                with result_tabs[0]:
                    st.subheader("📑 Detailed Analysis")
                    st.markdown(analysis_response.content if analysis_response.content else "No response generated.")

                with result_tabs[1]:
                    st.subheader("📌 Key Points Summary")
                    # Generate key points summary
                    _, _, _, team_coordinator = initialize_ai_agents()
                    if team_coordinator:
                        key_points_summary = team_coordinator.run(
                            f"Extract 5 key legal points from: {str(analysis_response.content)[:300]}..."
                        )
                        st.markdown(key_points_summary.content if key_points_summary.content else "No summary generated.")
                    else:
                        st.error("Team Coordinator agent not available")

                with result_tabs[2]:
                    st.subheader("📋 Recommendations")
                    # Generate recommendations
                    _, _, _, team_coordinator = initialize_ai_agents()
                    if team_coordinator:
                        recommendations_summary = team_coordinator.run(
                            f"Provide 3 specific legal recommendations from: {str(analysis_response.content)[:300]}..."
                        )
                        st.markdown(recommendations_summary.content if recommendations_summary.content else "No recommendations generated.")
                    else:
                        st.error("Team Coordinator agent not available")
else:
    st.warning("⚠️ Please upload a PDF document to begin analysis")
    st.info("The AI Legal Team will analyze your document once it's uploaded and processed.")