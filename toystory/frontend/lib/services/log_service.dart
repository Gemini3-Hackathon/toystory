import '../models/daily_log.dart';
import '../models/weekly_summary.dart';
import 'api_client.dart';

class LogService {
  final ApiClient _api;

  LogService(this._api);

  Future<List<DailyLog>> getLogs(String toyId, {String? date}) async {
    String path = '/logs/$toyId';
    if (date != null) path += '?date=$date';
    final result = await _api.get(path);
    final data = result['data'] as List;
    return data.map((j) => DailyLog.fromJson(j)).toList();
  }

  Future<List<WeeklySummary>> getSummary(String toyId) async {
    final result = await _api.get('/summary/$toyId');
    final data = result['data'] as List;
    return data.map((j) => WeeklySummary.fromJson(j)).toList();
  }
}
