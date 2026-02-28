import '../models/toy.dart';
import 'api_client.dart';

class ToyService {
  final ApiClient _api;

  ToyService(this._api);

  Future<List<Toy>> getToys() async {
    final result = await _api.get('/toys');
    final data = result['data'] as List;
    return data.map((j) => Toy.fromJson(j)).toList();
  }

  Future<Toy> getToy(String toyId) async {
    final result = await _api.get('/toys/$toyId');
    return Toy.fromJson(result['data']);
  }

  Future<Toy> createToy({
    required String photoPath,
    required String toyName,
    String childName = '',
  }) async {
    final result = await _api.multipartPost(
      '/toys',
      filePath: photoPath,
      fileField: 'photo',
      fields: {'toy_name': toyName, 'child_name': childName},
    );
    return Toy.fromJson(result['data']);
  }

  Future<void> deleteToy(String toyId) async {
    await _api.delete('/toys/$toyId');
  }
}
