from flask import Flask

def create_app():
    app = Flask(__name__)
    # app.config['UPLOAD_FOLDER'] = '/home/shenc/Desktop/study/Search-Engine/cache/'  # 文件存储路径
    app.config['BASE_PATH'] = '/home/shenc/Desktop/study/Search-Engine/cache/'
    # 注册蓝图
    from .routes import main
    app.register_blueprint(main)

    return app