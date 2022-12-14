from retrieval import *
from flask import Flask,  render_template
app = Flask(__name__,  # 如果指定的__name__模块没有找到,会把当前模块所在目录当成项目根目录。
            static_url_path="",  # 访问静态资源的url前缀, 默认值是static
            static_folder="",  # 静态文件的存放目录，默认就是static
            )
 

@app.route("/", methods=["GET", "POST"])
@app.route("/<question>", methods=["GET", "POST"])

def func(question=None):
    if question==None:
        answer=None
        length=0
    else:
        answer=QUERY(question,main_datas)
        length=len(answer)

    return render_template('index.html',  question=question, answer=answer,len=length)
 
 
if __name__ == "__main__":
    app.debug=True
    app.config["JSON_AS_ASCII"] = False
    app.run(host="127.0.0.1", port=4999)

