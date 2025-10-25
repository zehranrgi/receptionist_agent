"""
Barber Appointment Agent
A conversational AI agent that helps customers book appointments at a barber shop.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import openai
from tools import AVAILABLE_TOOLS


class BarberAppointmentAgent:
    """
    The main agent class that handles conversations and tool calling.
    
    This agent can:
    1. Understand customer requests
    2. Call appropriate tools to get information
    3. Book appointments
    4. Maintain conversation context
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the agent with OpenAI API key
        
        Args:
            api_key: OpenAI API key for GPT-5 model
        """
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        self.conversation_history = []
        self.current_appointment_context = {}
        
        # System prompt that defines the agent's role and capabilities
        self.system_prompt = """You are a helpful receptionist at The Greatest Barber Shop in Los Angeles. Your job is to help customers book appointments and answer questions about our services.

Available tools you can use:
- get_business_info(info_type): Get business hours, contact info, or address
- get_services(): Get all services and prices
- check_availability(date, duration_minutes): Check available time slots
- book_appointment(...): Book an appointment with customer details
- send_email_confirmation(...): Send confirmation email

Guidelines:
1. Always be friendly and professional
2. Ask for specific information when needed (name, phone, email for booking)
3. Check availability before booking
4. Confirm all details before finalizing appointments
5. If a time slot is not available, suggest alternatives
6. Always provide the appointment ID after successful booking
7. All prices are in USD
8. We're located in West Hollywood, Los Angeles

Current date: {current_date}"""

    def _call_openai(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Call OpenAI API with the given messages
        
        Args:
            messages: List of message dictionaries
            temperature: Controls randomness (0.0 to 1.0)
        
        Returns:
            Response from OpenAI
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-chat-latest", 
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I'm having trouble connecting to the AI service. Error: {str(e)}"

    def _extract_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract tool calls from the AI response
        """
        tool_calls = []
        
        # Look for both TOOL: pattern and [function()] pattern in the response
        tool_patterns = [
            r'TOOL:\s*(\w+)\((.*?)\)',  # TOOL: function() pattern
            r'\[(\w+)\((.*?)\)\]'        # [function()] pattern
        ]
        matches = []
        for pattern in tool_patterns:
            matches.extend(re.findall(pattern, response, re.DOTALL))
        
        for tool_name, args_str in matches:
            try:
                # Parse arguments
                if args_str.strip():
                    # Simple argument parsing - in a real system, you'd use a proper parser
                    args = []
                    if args_str.strip():
                        # Split by comma and clean up
                        arg_parts = [arg.strip().strip('"\'') for arg in args_str.split(',')]
                        args = []
                        for part in arg_parts:
                            # Try to convert to int or float if possible
                            try:
                                if '.' in part:
                                    args.append(float(part))
                                else:
                                    args.append(int(part))
                            except ValueError:
                                args.append(part)
                else:
                    args = []
                
                tool_calls.append({
                    "tool_name": tool_name,
                    "args": args
                })
            except Exception as e:
                print(f"Error parsing tool call: {e}")
                continue
        
        return tool_calls

    def _execute_tool(self, tool_name: str, args: List[Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given arguments
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool
        
        Returns:
            Result from the tool execution
        """
        if tool_name not in AVAILABLE_TOOLS:
            return {"error": f"Unknown tool: {tool_name}"}
        
        tool_info = AVAILABLE_TOOLS[tool_name]
        tool_function = tool_info["function"]
        
        try:
            # Call the tool function with the arguments
            if args:
                result = tool_function(*args)
            else:
                result = tool_function()
            
            return {
                "success": True,
                "result": result,
                "tool_name": tool_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }

    def _should_use_tools(self, user_message: str) -> bool:
        """
        Determine if the user message requires tool usage
        
        Args:
            user_message: The user's message
        
        Returns:
            True if tools should be used, False otherwise
        """
        # Keywords that suggest tool usage
        tool_keywords = [
            'randevu', 'appointment', 'book', 'rezervasyon',
            'fiyat', 'price', 'hizmet', 'service',
            'müsait', 'available', 'saat', 'time',
            'çalışma saatleri', 'hours', 'iletişim', 'contact'
        ]
        
        user_lower = user_message.lower()
        return any(keyword in user_lower for keyword in tool_keywords)

    def _build_messages(self, user_message: str) -> List[Dict[str, str]]:
        """
        Build the message list for OpenAI API
        
        Args:
            user_message: The user's current message
        
        Returns:
            List of message dictionaries for OpenAI API
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        system_prompt = self.system_prompt.format(current_date=current_date)
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        for entry in self.conversation_history[-10:]:  # Keep last 10 exchanges
            messages.append(entry)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages

    def _process_tool_results(self, tool_results: List[Dict[str, Any]]) -> str:
        """
        Process tool results and generate a response
        
        Args:
            tool_results: List of tool execution results
        
        Returns:
            Formatted response string
        """
        if not tool_results:
            return "I didn't find any specific information to help you with."
        
        response_parts = []
        
        for tool_result in tool_results:
            if not tool_result["success"]:
                response_parts.append(f"Error with {tool_result['tool_name']}: {tool_result['error']}")
                continue
            
            result = tool_result["result"]
            tool_name = tool_result["tool_name"]
            
            if tool_name == "get_services":
                services = result.get("services", [])
                if services:
                    response_parts.append("Here are our services and prices:")
                    for service in services:
                        response_parts.append(f"✂️ {service['name']} - ${service['price']} ({service['duration_minutes']} min)")
                    response_parts.append("\nWould you like to book an appointment?")
                else:
                    response_parts.append("Sorry, there was an issue retrieving our services.")
            
            elif tool_name == "check_availability":
                if result.get("available", False):
                    slots = result.get("available_slots", [])
                    duration = result.get("duration_minutes", 0)
                    date = result.get("date", "")
                    
                    response_parts.append(f"Here are our available times for {date} for a {duration}-minute appointment:")
                    for slot in slots[:10]:  # Show first 10 slots
                        response_parts.append(f"- {slot}")
                    if len(slots) > 10:
                        response_parts.append(f"... and {len(slots) - 10} more times")
                    response_parts.append("\nWhich time works best for you?")
                else:
                    response_parts.append(f"Sorry, we don't have any available slots for {result.get('date', '')}.")
                    response_parts.append("Would you like to try a different date?")
            
            elif tool_name == "book_appointment":
                if result.get("success", False):
                    appointment = result.get("appointment", {})
                    appointment_id = result.get("appointment_id", "")
                    
                    response_parts.append("🎉 Your appointment has been successfully booked!")
                    response_parts.append(f"📅 Date: {appointment['appointment']['date']}")
                    response_parts.append(f"🕐 Time: {appointment['appointment']['time']}")
                    response_parts.append(f"✂️ Services: {', '.join(appointment['appointment']['services'])}")
                    response_parts.append(f"💰 Total: ${appointment['appointment']['total_price']}")
                    response_parts.append(f"⏱️ Duration: {appointment['appointment']['duration_minutes']} minutes")
                    response_parts.append(f"🆔 Appointment ID: {appointment_id}")
                    response_parts.append("\nI've sent a confirmation email to your address. Is there anything else I can help you with?")
                else:
                    response_parts.append("Sorry, there was an error creating your appointment. Please try again.")
            
            elif tool_name == "get_business_info":
                if "working_hours" in result:
                    response_parts.append(f"Our business hours: {result['working_hours']}")
                elif "phone" in result:
                    response_parts.append(f"Contact us: {result['phone']}")
                elif "address" in result:
                    response_parts.append(f"Address: {result['address']}")
                else:
                    response_parts.append("Sorry, there was an issue retrieving our business information.")
        
        return "\n".join(response_parts)

    def chat(self, user_message: str) -> str:
        """
        Main chat method that processes user messages and returns responses
        
        Args:
            user_message: The user's message
        
        Returns:
            Agent's response
        """
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Build messages for OpenAI
        messages = self._build_messages(user_message)
        
        # Get initial response from OpenAI
        ai_response = self._call_openai(messages)
        
        # Check if we should use tools
        if self._should_use_tools(user_message):
            # Extract tool calls from AI response
            tool_calls = self._extract_tool_calls(ai_response)
            
            if tool_calls:
                # Execute tools
                tool_results = []
                for tool_call in tool_calls:
                    tool_name = tool_call["tool_name"]
                    args = tool_call["args"]
                    
                    print(f"🔧 Executing tool: {tool_name}({args})")
                    result = self._execute_tool(tool_name, args)
                    tool_results.append(result)
                
                # Process tool results and generate final response
                final_response = self._process_tool_results(tool_results)
            else:
                # No tools were called, use AI response directly
                final_response = ai_response
        else:
            # No tools needed, use AI response directly
            final_response = ai_response
        
        # Add agent response to conversation history
        self.conversation_history.append({"role": "assistant", "content": final_response})
        
        return final_response

    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
        self.current_appointment_context = {}


def main():
    """
    Main function to run the agent in terminal mode
    """
    # Load API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Initialize agent
    agent = BarberAppointmentAgent(api_key)
    
    print("🪒 Welcome to Elite Barber Shop in Los Angeles!")
    print("I'm your AI receptionist. How can I help you today?")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thank you for visiting Elite Barber Shop. Have a great day!")
                break
            
            if not user_input:
                continue
            
            # Get response from agent
            response = agent.chat(user_input)
            print(f"\nAgent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main()
