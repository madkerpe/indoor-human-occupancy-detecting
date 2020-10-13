from flask import Flask
from flask import render_template, redirect, url_for
from Container import Image, Video

# this contains 'display-name': 'URL (relative to static/video/)
# order in the list is used for menu-bar
content_list = [Video("MidSummit","MidSummit.mp4") ,Video("Cagsawa", "CagsawaRuins.mp4"),Image("test","stub.jpg")]


app=Flask(__name__)
@app.route('/')
def home():
    return redirect(url_for("index"))

@app.route('/index')
def index():
    return render_template("main.html", content_list = content_list)

@app.route('/content/<int:id>')
def content(id):
    if id >= len(content_list):
        return redirect(url_for("index"))
    item = content_list[id]
    if (isinstance(item,Video)):
        return render_template("video.html",video_path = item.path + content_list[id].filename, content_list = content_list)
    elif (isinstance(item,Image)):
        return render_template("Image.html",image_path = item.path + content_list[id].filename, content_list = content_list)
    else:
        return "type not found!"

if (__name__=='__main__'):
    app.run(debug=True)