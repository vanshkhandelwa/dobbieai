import os
import google.generativeai as genai
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        # Configure Google Generative AI
        self.api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        """Generate text using Gemini Pro"""
        try:
            if system_prompt:
                chat = self.model.start_chat(history=[
                    {"role": "user", "parts": [system_prompt]}
                ])
                response = chat.send_message(prompt)
            else:
                response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error in LLM service: {e}")
            return f"I encountered an issue while processing your request. Error: {str(e)}"
    
    def analyze_medical_data(self, data: Dict[str, Any]) -> str:
        """Analyze medical data and generate insights"""
        prompt = f"""
        Please analyze the following medical information and provide insights:
        
        Patient Information: {data.get('patient_info', 'N/A')}
        Medical History: {data.get('medical_history', 'N/A')}
        Recent Symptoms: {data.get('symptoms', 'N/A')}
        Recent Test Results: {data.get('test_results', 'N/A')}
        
        Provide a thoughtful analysis including possible conditions, recommended next steps, 
        and any important health considerations. Remember to mention this is not a definitive 
        medical diagnosis and the patient should consult with their healthcare provider.
        """
        
        return self.generate_text(prompt)
    
    def generate_appointment_summary(self, appointment_data: Dict[str, Any]) -> str:
        """Generate a summary for an appointment"""
        prompt = f"""
        Please create a concise appointment summary based on the following information:
        
        Doctor: {appointment_data.get('doctor_name', 'N/A')}
        Specialty: {appointment_data.get('specialization', 'N/A')}
        Patient: {appointment_data.get('patient_name', 'N/A')}
        Date & Time: {appointment_data.get('date_time', 'N/A')}
        Reason for Visit: {appointment_data.get('reason', 'N/A')}
        Diagnosis: {appointment_data.get('diagnosis', 'N/A')}
        Treatment: {appointment_data.get('treatment', 'N/A')}
        Follow-up: {appointment_data.get('follow_up', 'N/A')}
        
        Create a professional and clear summary that the patient can easily understand.
        """
        
        return self.generate_text(prompt)

llm_service = LLMService()