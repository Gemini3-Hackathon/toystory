import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import '../config/api_config.dart';

/// Talk Screen — Voice chat with toy character using WebView
class TalkScreen extends StatefulWidget {
  final String toyId;
  final String toyName;

  const TalkScreen({
    super.key,
    required this.toyId,
    required this.toyName,
  });

  @override
  State<TalkScreen> createState() => _TalkScreenState();
}

class _TalkScreenState extends State<TalkScreen> {
  late final WebViewController _controller;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageFinished: (url) {
            setState(() => _loading = false);
            // Inject toy configuration
            _controller.runJavaScript('''
              if (window.setToyConfig) {
                window.setToyConfig({
                  toyId: "${widget.toyId}",
                  toyName: "${widget.toyName}"
                });
              }
            ''');
          },
        ),
      )
      ..loadRequest(
        Uri.parse('${ApiConfig.talkWebUrl}/index.html?toyId=${widget.toyId}&toyName=${Uri.encodeComponent(widget.toyName)}'),
      );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.toyName}에게 말하기'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Stack(
        children: [
          WebViewWidget(controller: _controller),
          if (_loading)
            Container(
              color: Colors.white,
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      '${widget.toyName}을(를) 준비하는 중...',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
