import os
import sys
import requests
from dotenv import load_dotenv

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

def validate_github_token():
    """
    验证 GitHub Token 是否有效以及权限配置
    
    Returns:
        bool: Token 是否有效
    """
    # 加载环境变量文件
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("[ERROR] 未找到 GITHUB_TOKEN 环境变量")
        return False
    
    # 验证 token 基本有效性的请求头
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'note-taking-app/1.0'  # 添加 User-Agent
    }
    
    try:
        print("正在验证 GitHub Token...")
        
        # 检查用户信息
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            login = user_info.get('login', 'Unknown')
            print(f"[SUCCESS] Token 有效，用户: {login}")
            
            # 检查 token 类型和权限
            token_type = response.headers.get('X-GitHub-Token-Type', 'unknown')
            print(f"[INFO] Token 类型: {token_type}")
            
            # 检查是否为 Fine-grained token
            if token.startswith('github_pat_'):
                print("[INFO] 使用的是 Fine-grained personal access token")
            else:
                print("[WARNING] 建议使用 Fine-grained personal access token")
            
            # 检查用户的 Copilot 订阅状态
            print("正在检查 Copilot 权限...")
            copilot_response = requests.get(
                'https://api.github.com/copilot/billing', 
                headers=headers,
                timeout=10
            )
            
            if copilot_response.status_code == 200:
                print("[SUCCESS] Copilot API 权限正常")
                
                # 尝试获取 Copilot 使用情况
                billing_info = copilot_response.json()
                seat_breakdown = billing_info.get('seat_breakdown', {})
                total_seats = seat_breakdown.get('total', 0)
                print(f"[INFO] Copilot 座位数: {total_seats}")
                
            elif copilot_response.status_code == 404:
                print("[WARNING] 未找到 Copilot 订阅或权限不足")
            elif copilot_response.status_code == 403:
                print("[ERROR] Copilot API 权限被拒绝")
            else:
                print(f"[WARNING] Copilot API 权限检查失败，状态码: {copilot_response.status_code}")
                if copilot_response.text:
                    print(f"[DEBUG] 响应内容: {copilot_response.text}")
            
            # 检查速率限制
            rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'Unknown')
            rate_limit_reset = response.headers.get('X-RateLimit-Reset', 'Unknown')
            print(f"[INFO] API 剩余调用次数: {rate_limit_remaining}")
            
            return True
            
        elif response.status_code == 401:
            print("[ERROR] Token 无效或已过期")
            print("[HINT] 请检查 .env 文件中的 GITHUB_TOKEN 是否正确")
            return False
            
        elif response.status_code == 403:
            print("[ERROR] Token 权限不足")
            print("[HINT] 请确保 Token 具有必要的权限")
            return False
            
        else:
            print(f"[ERROR] API 请求失败，状态码: {response.status_code}")
            if response.text:
                print(f"[DEBUG] 响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("[ERROR] 请求超时，请检查网络连接")
        return False
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] 网络连接失败，请检查网络设置")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 网络请求错误: {str(e)}")
        return False
        
    except Exception as e:
        print(f"[ERROR] 未知错误: {str(e)}")
        return False

def test_copilot_api():
    """
    测试 GitHub Copilot API 的实际调用
    
    Returns:
        bool: 测试是否成功
    """
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("[ERROR] 未找到 GITHUB_TOKEN 环境变量")
        return False
    
    # Copilot Chat API 端点
    api_url = "https://api.github.com/copilot/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "note-taking-app/1.0"
    }
    
    # 简单的测试请求
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "你是一个有用的助手。"
            },
            {
                "role": "user",
                "content": "请说'Hello World'"
            }
        ],
        "model": "gpt-4o",  # 使用支持的模型
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        print("正在测试 Copilot Chat API...")
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"[DEBUG] API 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                print(f"[SUCCESS] Copilot API 测试成功")
                print(f"[RESPONSE] {content}")
                return True
            else:
                print("[WARNING] API 调用成功但返回内容为空")
                return False
                
        else:
            print(f"[ERROR] Copilot API 测试失败，状态码: {response.status_code}")
            print(f"[DEBUG] 响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Copilot API 测试异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("GitHub Token 验证工具")
    print("=" * 50)
    
    # 验证基本 token
    token_valid = validate_github_token()
    
    print("\n" + "=" * 50)
    
    if token_valid:
        print("基础验证通过，开始测试 Copilot API...")
        copilot_valid = test_copilot_api()
        
        if copilot_valid:
            print("\n[SUCCESS] 所有测试通过！可以正常使用 GitHub AI 服务。")
        else:
            print("\n[WARNING] Copilot API 测试失败，请检查权限配置。")
    else:
        print("\n[ERROR] Token 验证失败，请检查配置。")
    
    print("=" * 50)