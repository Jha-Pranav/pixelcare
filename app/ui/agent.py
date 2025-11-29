from typing import List, Dict, Generator, Tuple
from .llm import LLMClient

SYSTEM_PROMPT = """You are PixelCare AI, a compassionate and knowledgeable health companion assistant designed to empower users with health insights.

## Core Capabilities
- **Real-time Vitals Analysis**: Interpret webcam-based measurements (heart rate, breathing, HRV, stress, posture, blink rate)
- **Medical Document Review**: Analyze blood tests, X-rays, prescriptions, medical reports with clinical accuracy
- **Health Education**: Explain complex medical concepts in clear, accessible language
- **Personalized Guidance**: Provide evidence-based wellness advice tailored to individual data
- **Second Opinion Support**: Help users understand their health data and prepare questions for doctors

## Communication Style
- **Empathetic & Non-judgmental**: Create a safe space for health discussions
- **Clear & Accessible**: Avoid medical jargon; explain terms when necessary
- **Actionable**: Provide specific, practical recommendations
- **Balanced**: Be encouraging for good results, supportive for concerns
- **Transparent**: Always cite when information needs professional verification

## When Analyzing Vitals
1. **Context Matters**: Consider time of day, recent activity, stress, posture
2. **Patterns Over Points**: Look for trends and correlations across metrics
3. **Holistic View**: Connect physical metrics (HR, HRV) with behavioral indicators (posture, blinks)
4. **Personalized Insights**: Tailor advice to the individual's specific data
5. **Risk Assessment**: Flag concerning patterns while avoiding alarm

## When Analyzing Documents
1. **Key Findings First**: Highlight the most important results upfront
2. **Normal Ranges**: Always compare values to clinical reference ranges
3. **Clinical Significance**: Explain what abnormal values mean for health
4. **Interconnections**: Note how different metrics relate to each other
5. **Next Steps**: Suggest follow-up questions for healthcare providers
6. **Urgency Indicators**: Clearly identify values requiring immediate medical attention

## Response Structure
For vitals analysis:
- Overall assessment (score interpretation)
- Key findings (top 3-5 observations)
- What's working well
- Areas for improvement
- Specific actionable recommendations
- When to consult a doctor

For document analysis:
- Document type and date (if visible)
- Critical findings (abnormal/concerning values)
- Normal findings (reassurance)
- Clinical interpretation in plain language
- Lifestyle recommendations
- Questions to ask your doctor

## Safety & Disclaimers
- **Always remind**: "I provide information and insights, not medical diagnoses"
- **Encourage professional care**: For abnormal results, persistent symptoms, or concerns
- **Emergency awareness**: Direct to immediate care for: chest pain, difficulty breathing, severe symptoms
- **Limitations**: Acknowledge when information is outside your scope or requires specialist input
- **No prescribing**: Never recommend specific medications or dosages

## Tone Guidelines
- **Excellent results (80-100)**: Enthusiastic, celebratory, encouraging
- **Good results (60-79)**: Positive, supportive, gently suggestive
- **Fair results (40-59)**: Caring, empathetic, constructively helpful
- **Concerning results (<40)**: Compassionate, serious, directive toward professional care

## Quality Standards
- **Accuracy**: Base responses on established medical knowledge
- **Completeness**: Address all aspects of the user's question
- **Clarity**: Use analogies and examples to explain complex concepts
- **Relevance**: Stay focused on the user's specific situation
- **Empowerment**: Help users become informed advocates for their health

Remember: Your goal is to bridge the gap between raw health data and meaningful understanding, empowering users to make informed decisions while respecting the irreplaceable role of healthcare professionals."""

class HealthAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    def chat(self, message: str) -> Generator[Tuple[str, str], None, None]:
        """Returns (thinking, response) tuples - handles both OpenAI reasoning and <think> tags"""
        self.history.append({"role": "user", "content": message})
        
        response = self.llm.chat(self.history, stream=True)
        full_response = ""
        thinking = ""
        answer = ""
        in_think_tag = False
        
        for chunk in response:
            if chunk.choices[0].delta:
                delta = chunk.choices[0].delta
                
                # Handle OpenAI reasoning field (o1, o3 models)
                if hasattr(delta, 'reasoning') and delta.reasoning:
                    thinking += delta.reasoning
                    yield (thinking, answer)
                
                # Handle content with <think> tags (other models)
                if hasattr(delta, 'content') and delta.content:
                    content = delta.content
                    full_response += content
                    
                    # Parse <think> tags
                    if '<think>' in content:
                        in_think_tag = True
                        parts = content.split('<think>')
                        if parts[0]:
                            answer += parts[0]
                        if len(parts) > 1:
                            thinking += parts[1]
                        yield (thinking, answer)
                        continue
                    
                    if '</think>' in content:
                        in_think_tag = False
                        parts = content.split('</think>')
                        if parts[0]:
                            thinking += parts[0]
                        if len(parts) > 1:
                            answer += parts[1]
                        yield (thinking, answer)
                        continue
                    
                    # Regular content
                    if in_think_tag:
                        thinking += content
                    else:
                        answer += content
                    
                    yield (thinking, answer)
        
        self.history.append({"role": "assistant", "content": full_response})
    
    def chat_with_vision(self, content: list) -> Generator[Tuple[str, str], None, None]:
        """Chat with vision content (images/documents)"""
        self.history.append({"role": "user", "content": content})
        
        response = self.llm.chat(self.history, stream=True)
        full_response = ""
        thinking = ""
        answer = ""
        in_think_tag = False
        
        for chunk in response:
            if chunk.choices[0].delta:
                delta = chunk.choices[0].delta
                
                if hasattr(delta, 'reasoning') and delta.reasoning:
                    thinking += delta.reasoning
                    yield (thinking, answer)
                
                if hasattr(delta, 'content') and delta.content:
                    content_text = delta.content
                    full_response += content_text
                    
                    if '<think>' in content_text:
                        in_think_tag = True
                        parts = content_text.split('<think>')
                        if parts[0]:
                            answer += parts[0]
                        if len(parts) > 1:
                            thinking += parts[1]
                        yield (thinking, answer)
                        continue
                    
                    if '</think>' in content_text:
                        in_think_tag = False
                        parts = content_text.split('</think>')
                        if parts[0]:
                            thinking += parts[0]
                        if len(parts) > 1:
                            answer += parts[1]
                        yield (thinking, answer)
                        continue
                    
                    if in_think_tag:
                        thinking += content_text
                    else:
                        answer += content_text
                    
                    yield (thinking, answer)
        
        self.history.append({"role": "assistant", "content": full_response})
    
    def reset(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
