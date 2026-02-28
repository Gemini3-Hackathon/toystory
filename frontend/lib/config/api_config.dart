/// API Configuration for ToyTalk
class ApiConfig {
  // Android Emulator: use 10.0.2.2 instead of localhost
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';
  static const String wsUrl = 'ws://10.0.2.2:8000/ws/live';
  
  // Web Talk App URL (served by backend)
  static const String talkWebUrl = 'http://10.0.2.2:8000/talk-web';
  
  // For physical device, use your machine's IP:
  // static const String baseUrl = 'http://192.168.x.x:8000/api/v1';
}
