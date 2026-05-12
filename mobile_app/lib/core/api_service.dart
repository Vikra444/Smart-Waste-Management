import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000'; // Change to IP for physical device

  static Future<List<dynamic>> fetchTelemetry() async {
    final response = await http.get(Uri.parse('$baseUrl/telemetry'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    return [];
  }

  static Future<Map<String, dynamic>> predictWaste(String imagePath) async {
    // In real app, use MultipartRequest for image upload
    // For demo/mock bridge:
    return {
      "label": "RECYCLABLE",
      "confidence": 0.98,
      "guidance": "Blue Bin (Dry Waste)",
      "inference_time": 120
    };
  }

  static Future<Map<String, dynamic>> fetchOptimizedRoute() async {
    final response = await http.get(Uri.parse('$baseUrl/route'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    return {};
  }
}
