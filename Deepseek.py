from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import threading

app = Flask(__name__)

# 初始化 OpenAI 客户端
client = OpenAI(api_key="sk-6420bba0892f4be7ac066d109d8aa03b", base_url="https://api.deepseek.com")

# 提供前端页面
@app.route('/')
def index():
    return render_template('index.html')  # 渲染前端页面

@app.route('/api/deepseek', methods=['POST'])
def deepseek_api():
    try:
        # 获取用户输入
        user_input = request.json.get('message')
        if not user_input:
            return jsonify({'response': 'Please provide a valid question.'}), 400

        # 调用 Deepseek API
        def call_deepseek_api(user_input):
            try:
                response = client.chat.completions.create(
                    model='deepseek-chat',
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant"},
                        {"role": "user", "content": user_input},
                    ],
                    stream=True
                )

                full_response = ""
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        full_response += delta.content

                return full_response
            except Exception as e:
                return f"Error: {str(e)}"

        # 使用线程处理API调用
        result = [None]  # 使用列表存储结果，以便在线程中修改
        thread = threading.Thread(target=lambda: result.__setitem__(0, call_deepseek_api(user_input)))
        thread.start()
        thread.join()  # 等待线程完成

        # 返回结果
        return jsonify({'response': result[0]})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)