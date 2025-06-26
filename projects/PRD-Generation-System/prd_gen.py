from pathlib import Path
import openai
import anthropic
from typing import List
import base64




class PRDGenerationSystem:
    def __init__(self):
        self.chatgpt_api_key = "your_chatgpt_api_key_here"
        self.claude_api_key = "your_claude_api_key_here"
    
    def encode_pdf_to_base64(self, file_path: str) -> str:
        """Encode PDF file to base64 for API upload"""
        with open(file_path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')
    
    def get_prd_generation_prompt(self) -> str:
        """Get the core PRD generation prompt"""
        return """
        You are an expert Product Manager. Your task is to create a comprehensive Product Requirements Document (PRD) based on the provided information and context.

        A great PRD should include:

        ## 1. EXECUTIVE SUMMARY
        - Brief overview of the product/feature
        - Key business objectives
        - Success metrics

        ## 2. PROBLEM STATEMENT
        - What problem are we solving?
        - Who has this problem?
        - Why is this important now?

        ## 3. TARGET USERS & PERSONAS
        - Primary user segments
        - User personas and their needs
        - User journey considerations

        ## 4. PRODUCT GOALS & SUCCESS METRICS
        - Business objectives
        - Key Performance Indicators (KPIs)
        - Success criteria

        ## 5. PRODUCT REQUIREMENTS
        ### Functional Requirements
        - Core features and capabilities
        - User flows
        - Integration requirements

        Please create a detailed, actionable PRD that follows this structure and incorporates insights from any provided context documents.
        """
    
    def generate_chatgpt_prd(self, new_info_file: str, context_files: List[str] = None) -> str:
        """Generate PRD using ChatGPT with PDF context"""
        try:
            # Initialize OpenAI client with minimal parameters
            client = openai.OpenAI(
                api_key=self.chatgpt_api_key
            )
            
            # Build the message content
            message_content = [
                {
                    "type": "text",
                    "text": self.get_prd_generation_prompt()
                }
            ]
            
            # Add context PRDs if provided
            if context_files:
                message_content.append({
                    "type": "text",
                    "text": f"\n\nCONTEXT: Here are {len(context_files)} example PRD(s) for reference on style, format, and structure:"
                })
                
                for i, context_file in enumerate(context_files, 1):
                    if Path(context_file).suffix.lower() == '.pdf':
                        message_content.append({
                            "type": "text",
                            "text": f"\n--- CONTEXT PRD {i}: {Path(context_file).name} ---"
                        })
                        message_content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:application/pdf;base64,{self.encode_pdf_to_base64(context_file)}"
                            }
                        })
                    else:
                        # For non-PDF files, read as text
                        with open(context_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        message_content.append({
                            "type": "text",
                            "text": f"\n--- CONTEXT PRD {i}: {Path(context_file).name} ---\n{content}"
                        })
            
            # Add the new information to create PRD from
            message_content.append({
                "type": "text", 
                "text": f"\n\nNEW INFORMATION: Please create a PRD based on this new information/document:"
            })
            
            if Path(new_info_file).suffix.lower() == '.pdf':
                message_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:application/pdf;base64,{self.encode_pdf_to_base64(new_info_file)}"
                    }
                })
            else:
                # For non-PDF files, read as text
                with open(new_info_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                message_content.append({
                    "type": "text",
                    "text": f"Document content:\n{content}"
                })
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert Product Manager who creates comprehensive, actionable Product Requirements Documents (PRDs). Use the provided context PRDs as examples for style and structure, then create a new PRD based on the new information provided."
                    },
                    {
                        "role": "user",
                        "content": message_content
                    }
                ],
                max_tokens=4000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"❌ ChatGPT Error: {str(e)}"
        
    def generate_claude_prd(self, new_info_file: str, context_files: List[str] = None) -> str:
        """Generate PRD using Claude with PDF context"""  
        try:
            # Initialize Anthropic client with minimal parameters
            client = anthropic.Anthropic(
                api_key=self.claude_api_key
            )
            
            # Build the message content for Claude
            message_content = [
                {
                    "type": "text",
                    "text": self.get_prd_generation_prompt()
                }
            ]
            
            # Add context PRDs if provided
            if context_files:
                message_content.append({
                    "type": "text",
                    "text": f"\n\nCONTEXT: Here are {len(context_files)} example PRD(s) for reference on style, format, and structure:"
                })
                
                for i, context_file in enumerate(context_files, 1):
                    if Path(context_file).suffix.lower() == '.pdf':
                        message_content.append({
                            "type": "text",
                            "text": f"\n--- CONTEXT PRD {i}: {Path(context_file).name} ---"
                        })
                        message_content.append({
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": self.encode_pdf_to_base64(context_file)
                            }
                        })
                    else:
                        # For non-PDF files, read as text
                        with open(context_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        message_content.append({
                            "type": "text",
                            "text": f"\n--- CONTEXT PRD {i}: {Path(context_file).name} ---\n{content}"
                        })
            
            # Add the new information to create PRD from
            message_content.append({
                "type": "text", 
                "text": f"\n\nNEW INFORMATION: Please create a PRD based on this new information/document:"
            })
            
            if Path(new_info_file).suffix.lower() == '.pdf':
                message_content.append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": self.encode_pdf_to_base64(new_info_file)
                    }
                })
            else:
                # For non-PDF files, read as text
                with open(new_info_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                message_content.append({
                    "type": "text",
                    "text": f"Document content:\n{content}"
                })
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.3,
                system="You are an expert Product Manager who creates comprehensive, actionable Product Requirements Documents (PRDs). Use the provided context PRDs as examples for style and structure, then create a new PRD based on the new information provided.",
                messages=[
                    {
                        "role": "user",
                        "content": message_content
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            return f"❌ Claude Error: {str(e)}"
    
    def display_prds(self, chatgpt_prd: str, claude_prd: str):
        """Display both PRDs for comparison"""
        print("\n" + "="*80)
        print("📋 PRD COMPARISON")
        print("="*80)
        
        print("\n🤖 ChatGPT PRD:")
        print("-" * 40)

        print(chatgpt_prd)
        
        print("\n🧠 Claude PRD:")
        print("-" * 40) 

        print(claude_prd)
           
    def get_user_choice(self) -> str:
        """Get user's choice of which PRD is better"""
        while True:
            print("\nWhich PRD do you prefer?")
            print("1. ChatGPT PRD")
            print("2. Claude PRD") 
            print("3. Show PRDs again")
            print("4. Save both PRDs to files")
            
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                return "chatgpt"
            elif choice == "2":
                return "claude"
            elif choice == "3":
                return "show_again"
            elif choice == "4":
                return "save_both"
            else:
                print("❌ Invalid choice. Please enter 1-4.")
    
    def save_prd_to_file(self, prd_content: str, filename: str):
        """Save PRD content to a markdown file"""
        try:
            output_path = Path(f"generated_prds/{filename}")
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(prd_content)
            
            print(f"✅ PRD saved to: {output_path}")
            return str(output_path)
        
        except Exception as e:
            print(f"❌ Error saving PRD: {str(e)}")
            return None
    
    def process_prd_generation(self):
        """Main method to generate PRDs"""
        print("\n🚀 PRD GENERATION SYSTEM")
        print("="*50)
        
        # Get new information file
        new_info_file = input("Enter path to new information file (research, specs, etc.): ").strip()
        if not Path(new_info_file).exists():
            print(f"❌ File not found: {new_info_file}")
            return
        
        # Get context PRD files (optional)
        context_files = []
        print("\n📚 Context PRDs (optional - helps with style/format)")
        while True:
            context_file = input("Enter path to context PRD (or press Enter to skip): ").strip()
            if not context_file:
                break
            if Path(context_file).exists():
                context_files.append(context_file)
                print(f"✅ Added context: {Path(context_file).name}")
            else:
                print(f"❌ File not found: {context_file}")
        
        print(f"\n📊 Configuration:")
        print(f"  New info: {Path(new_info_file).name}")
        print(f"  Context PRDs: {len(context_files)} files")
        
        # Generate PRDs
        print("\n🤖 Generating ChatGPT PRD...")
        chatgpt_prd = self.generate_chatgpt_prd(new_info_file, context_files)
        
        print("🧠 Generating Claude PRD...")
        claude_prd = self.generate_claude_prd(new_info_file, context_files)
        
        # Display and get user choice
        while True:
            self.display_prds(chatgpt_prd, claude_prd)
            choice = self.get_user_choice()
            
            if choice == "show_again":
                continue
            elif choice == "save_both":
                # Save both PRDs
                base_name = Path(new_info_file).stem
                chatgpt_file = self.save_prd_to_file(chatgpt_prd, f"{base_name}_chatgpt_prd.md")
                claude_file = self.save_prd_to_file(claude_prd, f"{base_name}_claude_prd.md")
                
                print("\n💾 Both PRDs saved! You can:")
                print("1. Review them in your file manager")
                print("2. Edit them further")
                break
            else:
                # Save chosen PRD
                chosen_prd = chatgpt_prd if choice == "chatgpt" else claude_prd
                model_name = choice
                
                base_name = Path(new_info_file).stem
                saved_file = self.save_prd_to_file(chosen_prd, f"{base_name}_final_prd.md")
                
                if saved_file:
                    print(f"\n🎉 PRD generation complete!")
                    print(f"📄 Final PRD ({model_name}): {saved_file}")
                break

def main():
    """Main function to run the PRD generation system"""
    system = PRDGenerationSystem()
    
    while True:
        print("📋 PRD GENERATION SYSTEM")
        print("1. Generate new PRD")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == "1":
            system.process_prd_generation()
        
        elif choice == "2":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()