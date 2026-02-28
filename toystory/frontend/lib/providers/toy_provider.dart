import 'package:flutter/material.dart';
import '../models/toy.dart';
import '../services/api_client.dart';
import '../services/toy_service.dart';

class ToyProvider extends ChangeNotifier {
  final ToyService _service;
  List<Toy> _toys = [];
  bool _loading = false;
  String? _error;

  ToyProvider(ApiClient api) : _service = ToyService(api);

  List<Toy> get toys => _toys;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> loadToys() async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _toys = await _service.getToys();
    } catch (e) {
      _error = e.toString();
    }
    _loading = false;
    notifyListeners();
  }

  Future<Toy?> createToy({
    required String photoPath,
    required String toyName,
    String childName = '',
  }) async {
    try {
      final toy = await _service.createToy(
        photoPath: photoPath,
        toyName: toyName,
        childName: childName,
      );
      _toys.insert(0, toy);
      notifyListeners();
      return toy;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return null;
    }
  }

  Future<void> deleteToy(String toyId) async {
    try {
      await _service.deleteToy(toyId);
      _toys.removeWhere((t) => t.toyId == toyId);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
}
