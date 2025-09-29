import os
from openai import OpenAI
from typing import Optional


class GitHubAIService:
    """GitHub AI API service for content analysis"""
    
    def __init__(self):
        # 配置GitHub AI服务的端点和模型
        self.token = os.environ.get('GITHUB_TOKEN')
        self.endpoint = "https://models.github.ai/inference"
        self.model = "openai/gpt-4.1-mini"
        
        if not self.token:
            raise ValueError("GitHub token not found. Please set GITHUB_TOKEN environment variable.")
        
        # 初始化OpenAI客户端，使用GitHub AI端点
        self.client = OpenAI(
            base_url=self.endpoint,
            api_key=self.token,
        )
    
    def extract_key_information(self, content: str) -> str:
        """
        Extract key information from content using GitHub AI API
        
        Args:
            content (str): The content to analyze
            
        Returns:
            str: Extracted key information
        """
        prompt = f"""
请分析以下文档内容，并提取其中的关键信息。请按照以下格式整理信息：

📋 **主要内容摘要**
[提供文档的核心内容摘要]

🔑 **关键要点**
[列出3-5个主要要点]

📊 **重要数据/信息**
[提取重要的数据、日期、人名、地名等]

🎯 **行动项/任务**
[如果有的话，列出需要执行的任务或行动项]

💡 **关键洞察**
[提供有价值的洞察或结论]

文档内容：
{content}

请用中文回答，格式清晰易读。
"""
        
        try:
            # 使用OpenAI客户端发送请求
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的文档分析助手，擅长从各种文档中提取关键信息。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1500,
                top_p=1.0
            )
            
            # 提取返回内容
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                return "AI分析完成，但返回内容为空。"
                
        except Exception as e:
            # 处理OpenAI客户端异常
            error_str = str(e)
            if "401" in error_str or "Unauthorized" in error_str:
                return "❌ 认证失败，请检查GitHub Token是否有效"
            elif "429" in error_str or "rate limit" in error_str.lower():
                return "❌ API调用频率超限，请稍后重试"
            elif "timeout" in error_str.lower():
                return "❌ API请求超时，请稍后重试"
            else:
                return f"❌ 处理过程中发生错误: {str(e)}"


# Global instance
_ai_service = None

def get_ai_service() -> GitHubAIService:
    """Get or create AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = GitHubAIService()
    return _ai_service

def extract_key_info(content: str) -> str:
    """
    Extract key information from content
    
    Args:
        content (str): The content to analyze
        
    Returns:
        str: Extracted key information
    """
    try:
        service = get_ai_service()
        return service.extract_key_information(content)
    except ValueError as e:
        return f"❌ 配置错误: {str(e)}\n\n请确保设置了有效的GITHUB_TOKEN环境变量。"
    except Exception as e:
        return f"❌ 服务初始化失败: {str(e)}"