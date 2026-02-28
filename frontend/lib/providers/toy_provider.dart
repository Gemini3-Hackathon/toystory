import 'package:flutter/material.dart';
import '../models/toy.dart';
import '../services/api_service.dart';

/// Provider for managing toy state
class ToyProvider extends ChangeNotifier {
  List<Toy> _toys = [];
  bool _loading = false;
  String? _error;

  List<Toy> get toys => _toys;
  bool get loading => _loading;
  String? get error => _error;

  final _api = ApiService();

  Future<void> loadToys() async {
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      _toys = await _api.getToys();
    } catch (e) {
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<Toy> createToy({required String name, String? photoBase64}) async {
    final toy = await _api.createToy(name: name, photoBase64: photoBase64);
    _toys.insert(0, toy);
    notifyListeners();
    return toy;
  }
}
