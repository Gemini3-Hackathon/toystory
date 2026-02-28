import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/toy.dart';

/// API Service for ToyTalk backend
class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  // --- Toys ---
  
  Future<List<Toy>> getToys({String parentId = 'parent-001'}) async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/toys?parent_id=$parentId'),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['success'] == true) {
        return (data['data'] as List).map((j) => Toy.fromJson(j)).toList();
      }
    }
    throw Exception('Failed to load toys');
  }

  Future<Toy> getToy(String toyId) async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/toys/$toyId'),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['success'] == true) {
        return Toy.fromJson(data['data']);
      }
    }
    throw Exception('Failed to load toy');
  }

  Future<Toy> createToy({
    required String name,
    String? photoBase64,
    String parentId = 'parent-001',
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/toys'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'photo_base64': photoBase64,
        'parent_id': parentId,
      }),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['success'] == true) {
        return Toy.fromJson(data['data']);
      }
    }
    throw Exception('Failed to create toy');
  }

  // --- Talk ---
  
  Future<Map<String, dynamic>> talk({
    required String toyId,
    required String message,
    String? sessionId,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/talk'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'toy_id': toyId,
        'message': message,
        'session_id': sessionId,
      }),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['success'] == true) {
        return data['data'];
      }
    }
    throw Exception('Failed to talk');
  }

  // --- Logs ---
  
  Future<Map<String, dynamic>> getLogs(String toyId) async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/logs/$toyId'),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['success'] == true) {
        return data['data'];
      }
    }
    throw Exception('Failed to load logs');
  }

  // --- Summary ---
  
  Future<Map<String, dynamic>> getSummary(String toyId) async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/summary/$toyId'),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['success'] == true) {
        return data['data'];
      }
    }
    throw Exception('Failed to load summary');
  }
}
