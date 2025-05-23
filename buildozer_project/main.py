
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.webview import WebView

class WebViewApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        webview = WebView(url="https://workspace.ruanlouco231.repl.co")
        layout.add_widget(webview)
        return layout

if __name__ == '__main__':
    WebViewApp().run()
