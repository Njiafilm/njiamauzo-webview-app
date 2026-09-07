from kivy.app import App
from kivy.uix.widget import Widget
from kivy.utils import platform

class NjiaMauzoApp(App):
    def build(self):
        if platform == "android":
            from jnius import autoclass
            from android.runnable import run_on_ui_thread

            WebView = autoclass('android.webkit.WebView')
            WebViewClient = autoclass('android.webkit.WebViewClient')
            activity = autoclass('org.kivy.android.PythonActivity').mActivity

            @run_on_ui_thread
            def load_webview():
                webview = WebView(activity)
                webview.getSettings().setJavaScriptEnabled(True)
                webview.getSettings().setDomStorageEnabled(True)
                webview.setWebViewClient(WebViewClient())
                webview.loadUrl("https://njiamauzo-afrika.onrender.com/")
                activity.setContentView(webview)

            load_webview()
        return Widget()

NjiaMauzoApp().run()
