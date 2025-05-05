import streamlit as st
import os
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from io import BytesIO
from datetime import datetime
import json
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

# Set environment variable for Google Cloud authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "test.json"


# Set your Google Gemini API key here
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


st.set_page_config(layout="wide")


# Define questions and their corresponding options with scores
questions = {
  "Field Intelligence & Real-World Insights": [
    {
      "question": "1. How effectively is your organization capturing real-world insights from doctor and chemist visits?",
      "options": {
        "(a) Minimal - No systematic collection of field insights": 0,
        "(b) Basic - Manual documentation with limited utilization": 1,
        "(c) Moderate - Structured collection with partial digital transformation": 2,
        "(d) Advanced - Comprehensive digital capture with AI-enabled analysis": 3
      }
    },
    {
      "question": "2. To what extent are voice notes and unstructured data from field teams converted into actionable insights?",
      "options": {
        "(a) Not utilized - Voice data rarely captured or analyzed": 0,
        "(b) Limited - Basic transcription without systematic analysis": 1,
        "(c) Developing - Regular transcription with semi-automated analysis": 2,
        "(d) Sophisticated - Automated transcription with AI-powered insights extraction": 3
      }
    },
    {
      "question": "3. How effectively is your organization utilizing GenAI models to analyze field intelligence data?",
      "options": {
        "(a) <10% utilization - Minimal AI integration for field data": 0,
        "(b) 10-30% utilization - Basic AI implementation for specific insights": 1,
        "(c) 31-60% utilization - Moderate AI integration across multiple field data types": 2,
        "(d) >60% utilization - Extensive AI-powered analysis of field intelligence": 3
      }
    }
  ],
 
  "Domain-Specific AI Applications": [
    {
      "question": "4. How effectively is AI employed to identify and adapt to evolving pharmaceutical trends and insights?",
      "options": {
        "(a) Not implemented - No dynamic parameter identification": 0,
        "(b) Basic application - Limited trend identification capabilities": 1,
        "(c) Moderate implementation - Regular trend identification with some adaptation": 2,
        "(d) Advanced system - Agentic AI with dynamic parameter identification": 3
      }
    },
    {
      "question": "5. To what extent are your AI systems customized specifically for pharmaceutical domain knowledge?",
      "options": {
        "(a) Generic AI systems with no domain customization": 0,
        "(b) Limited customization for basic pharmaceutical terminology": 1,
        "(c) Moderate domain adaptation with pharmaceutical-specific training": 2,
        "(d) Comprehensive domain-specific models with deep pharmaceutical knowledge": 3
      }
    },
    {
      "question": "6. How sophisticated is your organization's use of AI for persona analysis in healthcare professional engagement?",
      "options": {
        "(a) Not utilized - Traditional segmentation approaches only": 0,
        "(b) Basic implementation - Simple AI-based segmentation": 1,
        "(c) Moderate utilization - AI-driven persona development": 2,
        "(d) Advanced application - Dynamic persona analysis with behavioral insights": 3
      }
    }
  ],


  "Data Processing & Quality": [
    {
      "question": "7. How effectively does your organization maintain consistency and accuracy when processing large volumes of voice data?",
      "options": {
        "(a) Inconsistent quality with significant error rates": 0,
        "(b) Basic quality control with manual verification": 1,
        "(c) Structured quality assurance with moderate consistency": 2,
        "(d) Advanced quality management with high accuracy at scale": 3
      }
    },
    {
      "question": "8. To what extent has your organization implemented vector databases for efficient retrieval of pharmaceutical insights?",
      "options": {
        "(a) Not implemented - Traditional databases only": 0,
        "(b) Early exploration - Limited vector search capabilities": 1,
        "(c) Partial implementation - Vector databases for select applications": 2,
        "(d) Full implementation - Comprehensive vector search infrastructure": 3
      }
    },
    {
      "question": "9. How sophisticated is your transcription capability for converting field audio into analyzable text?",
      "options": {
        "(a) Basic or non-existent - Limited transcription capabilities": 0,
        "(b) Standard transcription with moderate accuracy": 1,
        "(c) Advanced transcription with multilingual support": 2,
        "(d) High-performance transcription with contextual understanding": 3
      }
    }
  ],


  "User Experience & Adoption": [
    {
      "question": "10. How would you rate the user experience of AI tools for your field teams and managers?",
      "options": {
        "(a) Complex and difficult to use, limiting adoption": 0,
        "(b) Functional but requiring significant training": 1,
        "(c) User-friendly with moderate learning curve": 2,
        "(d) Highly intuitive with excellent usability driving widespread adoption": 3
      }
    },
    {
      "question": "11. To what degree can users interact conversationally with your data systems for instant analysis?",
      "options": {
        "(a) No conversational capabilities - Traditional query methods only": 0,
        "(b) Limited chat functionality with basic responses": 1,
        "(c) Moderate conversational abilities for standard queries": 2,
        "(d) Advanced conversational AI with deep analytical capabilities": 3
      }
    },
    {
      "question": "12. How effectively are pre-built AI modules deployed for common pharmaceutical use cases?",
      "options": {
        "(a) Not available - Custom solutions required for each use case": 0,
        "(b) Limited availability - Basic modules with minimal customization": 1,
        "(c) Moderate deployment - Several modules with configuration options": 2,
        "(d) Comprehensive library - Extensive pre-built modules with deep customization": 3
      }
    }
  ],


  "Integration & Scalability": [
    {
      "question": "13. How well integrated are your AI systems with existing pharmaceutical workflows and processes?",
      "options": {
        "(a) Minimal integration - AI systems operate in isolation": 0,
        "(b) Partial integration - Basic connections to select workflows": 1,
        "(c) Substantial integration - AI embedded in multiple critical processes": 2,
        "(d) Seamless integration - AI fully incorporated into daily operations": 3
      }
    },
    {
      "question": "14. How effectively can your AI infrastructure scale to accommodate growing volumes of field data?",
      "options": {
        "(a) Limited scalability - Performance issues with increased data": 0,
        "(b) Moderate scalability - Can handle growth with some constraints": 1,
        "(c) Good scalability - Designed for significant data volume increases": 2,
        "(d) Excellent scalability - Robust architecture for enterprise-scale data": 3
      }
    },
    {
      "question": "15. How comprehensively does your organization secure sensitive data in AI applications?",
      "options": {
        "(a) Basic security measures with significant vulnerabilities": 0,
        "(b) Standard security protocols with some gaps": 1,
        "(c) Advanced security framework with strong protections": 2,
        "(d) Enterprise-grade security with complete compliance coverage": 3
      }
    }
  ]
}


maturity_levels = [
    (31, 45, "Advanced - Strategically Optimized"),  # Next 33% score range: Strong AI application and data practices, with clear strategic direction.
    (16, 30, "Emerging - Building Foundations"),  # Middle 33% score range: Solid AI capabilities and data maturity, integrated into critical pharma functions.
    (0, 15, "Novice - Exploring Opportunities")  # Bottom 33% score range: Early-stage or limited adoption of AI, working on foundational capabilities.
]


# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "total_score" not in st.session_state:
    st.session_state.total_score = 0
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "user_info" not in st.session_state:
    st.session_state.user_info= {}


# Function to save data to BigQuery
def save_to_bigquery(user_info, total_score, maturity_level, responses, recommendations):
    client = bigquery.Client()
    dataset_id = "audit"  # Replace with your dataset ID
    table_id = "auditplus"  # Replace with your table name


    # Prepare responses as JSON
    response_json = json.dumps(responses, indent=2)


    rows_to_insert = [{
        "timestamp": datetime.now().isoformat(),
        "name": user_info["Name"],
        "company_name": user_info["Company Name"],
        "about_company": user_info["About"],
        "email": user_info["Email"],
        "domain": user_info["Domain"],
        "data_team_size": user_info["Data Team Size"],
        "ai_team_size": user_info["AI Team Size"],
        "organization_size": user_info["Organization Size"],
        "annual_revenue": user_info["Annual Revenue"],
        "customer_type": user_info["Customer Type"],
        "data_volume": user_info["Data Volume"],
        "ai_leadership_support": user_info["AI Leadership Support"],
        "total_score": total_score,
        "maturity_level": maturity_level,
        "reponse": response_json,
        "recommendations": recommendations  # Include recommendations here
    }]


    table_ref = f"{dataset_id}.{table_id}"
    print(table_ref)
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    print(errors)


    if errors == []:
         st.success("Here's an overview of our findings. Download the PDF now! A detailed report will be provided later.")
    else:
        st.error(f"A detailed report will be provided later.")


# Function to generate recommendations
from datetime import datetime


def generate_recommendations(user_info, total_score, maturity_level, assessment_json):
    from datetime import datetime
    current_date = datetime.now().strftime("%d-%B-%Y")


    prompt = f"""
You are acting as a Senior Consultant specializing in AI and Data Maturity for the Pharmaceutical Industry.


Today’s Date: {current_date}


The organization has completed a domain-specific assessment designed to evaluate its readiness for advanced AI integration through **Valence Pharma GPT** — a purpose-built GenAI solution for Pharma that transforms unstructured field insights into searchable, actionable, and multilingual intelligence.


---


### 🔍 What is Valence Pharma GPT?
Valence Pharma GPT is a secure, configurable AI assistant that enables pharma organizations to:
- Upload voice and media files from field visits or internal teams.
- Transcribe those files with **multilingual and pharma-specific accuracy**.
- Interact with the content using **chat-based Q&A** over transcripts.
- Search across thousands of conversations using **vector database indexing (Qdrant)**.
- Extract real-world insights across therapeutic areas, product feedback, regulatory challenges, and more.


For live product access and demos, visit: [https://valenceai.io](https://valenceai.io)


---


### 📊 Assessment Coverage
The following capabilities were evaluated, with each question scored on a 0–3 scale (0 = Minimal, 3 = Advanced):


- Field Intelligence & Real-World Insights  
- Domain-Specific AI Applications  
- Data Processing & Quality  
- User Experience & Adoption  
- Integration & Scalability  


**Organization Profile:**
- **Name**: {user_info.get('Company Name')}
- **Domain**: {user_info.get('Domain')}
- **Size**: {user_info.get('Organization Size')}
- **Annual Revenue**: {user_info.get('Annual Revenue')}
- **Data Team Size**: {user_info.get('Data Team Size')}
- **AI Team Size**: {user_info.get('AI Team Size')}
- **AI Leadership Support**: {user_info.get('AI Leadership Support')}
- **Regulatory Compliance**: {user_info.get('Regulatory Compliance')}
- **Clinical Trials Data Handling**: {user_info.get('Clinical Trials Data')}
- **Customer Type**: {user_info.get('Customer Type')}
- **Data Volume**: {user_info.get('Data Volume')}


**Assessment Score**: {total_score} / 45  
**Maturity Level**: {maturity_level}


---


### 🎯 Your Objective:
Using the organization’s profile and assessment results, generate a maturity diagnosis and a structured action plan using **only the capabilities of Valence Pharma GPT**.


Focus Areas:
1. Identify maturity level and what it means in the pharma data transformation journey.
2. Highlight top strengths based on high-scoring capabilities.
3. Pinpoint bottlenecks in AI utilization or unstructured data analysis.
4. Generate recommendations across:
   - **Short-Term (0–6 months)**: Quick wins aligned with onboarding Valence GPT (e.g., uploading voice logs, generating transcripts).
   - **Medium-Term (6–18 months)**: Strategic adoption of multilingual transcription, searchable insights, or cross-conversation pattern mining.
   - **Long-Term (18+ months)**: Full pipeline automation from field voice input to insight delivery and compliance reporting.


**Do not invent new modules or capabilities. Only refer to features described in Valence Pharma GPT’s current documentation.**


Your tone should be:
- Strategic and pharma-specific
- Clear, executive-style
- Focused on Valence Pharma GPT as the transformation enabler


Conclude with a call to explore [https://valenceai.io](https://valenceai.io) to begin their adoption pathway.
"""


    main_instruction = """
### Structure your output under these sections:


---


### **About Valence Pharma GPT**
Valence Pharma GPT is a secure, configurable AI assistant that enables pharma organizations to:
- Upload voice and media files from field visits or internal teams.
- Transcribe those files with **multilingual and pharma-specific accuracy**.
- Interact with the content using **chat-based Q&A** over transcripts.
- Search across thousands of conversations using **vector database indexing (Qdrant)**.
- Extract real-world insights across therapeutic areas, product feedback, regulatory challenges, and more.


For live product access and demos, visit: [https://valenceai.io](https://valenceai.io)


### **Overview**
- Interpret the organization’s current standing based on the score and profile.
- Explain how this reflects their AI maturity across field insights, quality, and regulatory intelligence.


---


### **Strengths**
- Highlight the top 2–3 scoring categories.
- Comment on team readiness or existing digital maturity if relevant.


---


### **Gaps**
- Analyze the lowest-scoring areas.
- Focus on where voice insights, regulatory document extraction, or field feedback structuring are lacking.


---


### **Recommendations**


#### Short-Term (0–6 Months)
- Upload existing voice recordings of field visits to Valence Pharma GPT.
- Generate multilingual, pharma-specific transcripts.
- Begin using chat-based querying to summarize key takeaways.


#### Medium-Term (6–18 Months)
- Start indexing field transcripts for thematic search using vector-powered Qdrant search.
- Tag common product feedback or regulatory risk mentions using GPT-powered auto-tagging.
- Enable multilingual interaction across regions for local sales insights.


#### Long-Term (18+ Months)
- Move toward complete automation: from field voice note to dashboard-ready insights.
- Establish internal SOPs to ingest voice logs directly into the Valence GPT portal for insights.
- Automate PSUR contributions and multilingual summaries from field medical data.


---




"""


    prompt += main_instruction
    model = genai.GenerativeModel('gemini-1.5-flash')
    messages = [{"role": "user", "parts": prompt}]
    response = model.generate_content(messages)
    return response.text






#UserInfo
if st.session_state.page == 0:
    st.markdown('<div style="text-align: right;"><img src="https://erp.atriina.com/files/Atrina_erp_Blue_Logo.png" alt="Atrina Logo" width="100" height="100" style="display: inline-block;"/></div>', unsafe_allow_html=True)
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTQLPHelmaulHqfeQuGbpwYWoUbcYKWQqRBqQ&s", width=100)
    st.title("PHARMA AI & DATA MATURITY ASSESSMENT")


    st.header("User Information")


    name = st.text_input("Name")
    company_name = st.text_input("Organization Name")
    about_company = st.text_input("About Your Organization (e.g., product types, therapeutic areas)")
    email = st.text_input("Business Email ID")


    domain = st.selectbox(
        "Domain",
        [
            "Pharmaceuticals",
            "Biotechnology",
            "Medical Devices",
            "Healthcare Providers",
            "CRO (Contract Research Organizations)"
        ]
    )


    data_team_size = st.selectbox(
        "Size of Data Team (Analytics and Engineering)",
        ["None", "1-5", "6-10", "11-20", "21-50", "51+"]
    )
   
    ai_team_size = st.selectbox(
        "Size of AI Team",
        ["None", "1-5", "6-10", "11-20", "21-50", "51+"]
    )


    org_size = st.selectbox(
        "Current size of your organization",
        [
            "Less than 50 employees",
            "51-200 employees",
            "201-500 employees",
            "501-1000 employees",
            "Over 1000 employees"
        ]
    )


    annual_revenue = st.selectbox(
        "Organization’s annual revenue in INR (Crores)",
        [
            "Less than ₹10 Crores",
            "₹10 Crores - ₹50 Crores",
            "₹50 Crores - ₹200 Crores",
            "₹200 Crores - ₹1000 Crores",
            "Over ₹1000 Crores"
        ]
    )


    customer_type = st.selectbox(
        "Type of customers your organization primarily serves",
        [
            "B2B (Business to Business)",
            "B2C (Business to Consumer)",
            "Both B2B and B2C",
            "Government or Public Sector",
            "Healthcare Providers",
            "Pharma Partners (e.g., other pharma companies, suppliers)"
        ]
    )


    data_volume = st.selectbox(
        "Data Volume typically generated or processed on a daily basis",
        [
            "Less than 1GB",
            "1GB - 10GB",
            "10GB - 100GB",
            "100GB - 1TB",
            "More than 1TB"
        ]
    )


    clinical_trials_data = st.selectbox(
        "Does your organization deal with clinical trials data?",
        ["Yes", "No"]
    )


    regulatory_compliance = st.selectbox(
        "Is your organization compliant with regulatory frameworks (e.g., FDA, EMA)?",
        ["Yes", "No", "Partially"]
    )


    ai_leadership_support = st.selectbox(
        "Leadership Support for AI",
        [
            "High commitment – AI is a core part of our business strategy",
            "Moderate commitment – AI is growing but not yet fully integrated",
            "Limited commitment – AI is explored but not a priority",
            "No commitment – AI is not part of our business strategy"
        ]
    )


    if st.button("Start Assessment"):
        st.session_state.user_info = {
            "Name": name,
            "Company Name": company_name,
            "About": about_company,
            "Email": email,
            "Domain": domain,
            "Data Team Size": data_team_size,
            "AI Team Size": ai_team_size,
            "Organization Size": org_size,
            "Annual Revenue": annual_revenue,
            "Customer Type": customer_type,
            "Data Volume": data_volume,
            "Clinical Trials Data": clinical_trials_data,
            "Regulatory Compliance": regulatory_compliance,
            "AI Leadership Support": ai_leadership_support
        }
        st.session_state.page = 1
        st.rerun()
# Step 2: Display Questions
elif st.session_state.page == 1:
    total_questions = sum(len(category) for category in questions.values())
    progress = (st.session_state.current_question_index + 1) / total_questions
    st.progress(progress)


    if st.session_state.current_question_index < total_questions:
        current_question_idx = st.session_state.current_question_index
        category_names = list(questions.keys())


        # Find current category and question
        question_count = 0
        current_category = None
        current_question = None
        for category in category_names:
            for q in questions[category]:
                if question_count == current_question_idx:
                    current_category = category
                    current_question = q
                    break
                question_count += 1
            if current_question is not None:
                break


        # Display current question and options
        st.markdown(f"### {current_category}")
        st.markdown(f"**{current_question['question']}**")


        if current_question.get("multiple_choice", False):
            response = st.multiselect(
                "Select all that apply:",
                options=list(current_question['options'].keys()),
                default=st.session_state.responses.get(current_question['question'], []),
                key=f"question_{current_question_idx}"
            )
        else:
            response = st.radio(
                "Select your response:",
                options=list(current_question['options'].keys()),
                index=list(current_question['options'].keys()).index(
                    st.session_state.responses.get(current_question['question'], list(current_question['options'].keys())[0])
                ) if current_question['question'] in st.session_state.responses else 0,
                key=f"question_{current_question_idx}"
            )


        col1, col2 = st.columns([0.03, 0.3])
        with col1:
            if st.button("Previous"):
                if st.session_state.current_question_index > 0:
                    st.session_state.current_question_index -= 1
                    st.rerun()
        with col2:
            if st.session_state.current_question_index == total_questions - 1:
                if st.button("Submit"):
                    if current_question.get("multiple_choice", False):
                        total_score = sum([current_question['options'].get(r, 0) for r in response])
                        st.session_state.responses[current_question['question']] = response
                    else:
                        total_score = current_question['options'][response]
                        st.session_state.responses[current_question['question']] = response


                    st.session_state.total_score += total_score
                    st.session_state.page = 2
                    st.rerun()
            else:
                if st.button("Next"):
                    if current_question.get("multiple_choice", False):
                        total_score = sum([current_question['options'].get(r, 0) for r in response])
                        st.session_state.responses[current_question['question']] = response
                    else:
                        total_score = current_question['options'][response]
                        st.session_state.responses[current_question['question']] = response


                    st.session_state.total_score += total_score
                    st.session_state.current_question_index += 1
                    st.rerun()




# Step 3: Results and Recommendations
elif st.session_state.page == 2:
    total_score = st.session_state.total_score
    user_info = st.session_state.user_info


    def get_maturity_level(score):
        for min_score, max_score, level in maturity_levels:
            if min_score <= score <= max_score:
                return level
        return "Undefined"


    maturity_level = get_maturity_level(total_score)
    # Show a loading spinner while generating recommendations
    with st.spinner("Generating recommendations..."):
        # Prepare JSON for responses
        assessment_json = json.dumps(st.session_state.responses, indent=2)


        # Generate Recommendations
        recommendations = generate_recommendations(user_info, total_score, maturity_level, assessment_json)


    # Once recommendations are ready, display results
   
    def get_score_distribution_info():
     return (
        "Score Distribution for Maturity Levels:\n"
        "31-45: Advanced - Strategically Optimized\n"
        "16-30: Emerging - Building Foundations\n"
        "0-15: Novice - Exploring Opportunities"
    )


    st.write("## Pharma Assessment Results")
    st.markdown(f"""<div style="display: flex; align-items: center;"><span><b>Maturity Level:</b> {maturity_level}</span><img src="https://img.icons8.com/ios-filled/20/007BFF/info.png" style="margin-left: 8px; cursor: pointer;" title="{get_score_distribution_info()}"></div>""", unsafe_allow_html=True)
    st.write(f"**Total Score:** {total_score} / 45")  # Updated line to show score out of 120
   


    # Append questions and answers for display
    # st.write("### Your Responses:")
    # for question, answer in st.session_state.responses.items():
    #     st.write(f"**{question}:** {answer}")


    st.write("### Recommendations")
    st.write(recommendations)


    # Save responses and recommendations to BigQuery
    save_to_bigquery(user_info, total_score, maturity_level, st.session_state.responses, recommendations)


    # Generate PDF
    def create_pdf(user_info, total_score, maturity_level, recommendations):
        from io import BytesIO
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4


        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []


        # Title
        title = Paragraph("Pharma Assessment Report", styles["Title"])
        elements.append(title)
        elements.append(Spacer(1, 12))


        # Organization Information
       
        elements.append(Paragraph(f"Company Name: {user_info['Company Name']}", styles["Normal"]))
        if 'Department' in user_info:
            elements.append(Paragraph(f"Department: {user_info['Department']}", styles["Normal"]))
        if 'Contact Person' in user_info:
            elements.append(Paragraph(f"Contact Person: {user_info['Contact Person']}", styles["Normal"]))


        elements.append(Spacer(1, 12))


        # Add a Date field
        from datetime import date
        elements.append(Paragraph(f"Date: {date.today().strftime('%Y-%m-%d')}", styles["Normal"]))


        elements.append(Spacer(1, 12))
       
        # Assessment Results
        assessment_title = Paragraph("Assessment Results", styles["Heading1"])
        elements.append(assessment_title)


        elements.append(Paragraph(f"Total Score: {total_score} / 45", styles["Normal"]))
        elements.append(Paragraph(f"Maturity Level: {maturity_level}", styles["Normal"]))


        elements.append(Spacer(1, 12))


        # Recommendations Section
        recommendations_title = Paragraph("Recommendations", styles["Heading1"])
        elements.append(recommendations_title)


        # Process Recommendations
        def clean_text(text):
            text = text.replace("##", "").replace("**", "").replace("#", "")
            return text


        clean_recommendations = clean_text(recommendations)
        for line in clean_recommendations.split('\n'):
            if line.strip().startswith("*"):
                line = line.replace("*", "•", 1)  # Replace '*' with '•' for bullets
            elements.append(Paragraph(line.strip(), styles["Normal"]))
            elements.append(Spacer(1, 12))


        doc.build(elements)
        buffer.seek(0)
        return buffer




    # Generate download button with dynamic label




    pdf_buffer = create_pdf(user_info, total_score, maturity_level, recommendations)
    st.download_button(
        label=f"Download Pharma Assessment Report - {user_info['Company Name']}.pdf",
        data=pdf_buffer,
        file_name=f"{user_info['Company Name']}_Pharma_Assessment_Report.pdf",
        mime="application/pdf"
    )
