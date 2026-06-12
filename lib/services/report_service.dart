import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/report_model.dart';

/// Service to communicate with your FastAPI/LangGraph backend.
/// The backend should expose POST /generate-report
/// See README for the expected FastAPI wrapper code.
class ReportService {
  // Change this to your actual backend URL
  static const String baseUrl = 'http://localhost:8000';

  /// Calls the orchestrator endpoint and streams back section updates.
  /// Returns a Stream of ReportState updates.
  static Stream<ReportState> generateReport(String topic) async* {
    final state = ReportState(
      topic: topic,
      status: GenerationStatus.planning,
    );
    yield state;

    try {
      // Step 1: Plan sections
      final planResponse = await http.post(
        Uri.parse('$baseUrl/plan-sections'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'topic': topic}),
      );

      if (planResponse.statusCode != 200) {
        throw Exception('Planning failed: ${planResponse.body}');
      }

      final planData = jsonDecode(planResponse.body) as Map<String, dynamic>;
      final sectionsList = planData['sections'] as List;
      final sections = sectionsList.map((s) {
        return ReportSection(
          name: s['name'] as String,
          description: s['description'] as String,
          status: SectionStatus.pending,
        );
      }).toList();

      yield state.copyWith(
        sections: sections,
        status: GenerationStatus.writing,
      );

      // Step 2: Write each section (parallel on server, streamed here)
      final updatedSections = List<ReportSection>.from(sections);

      // Mark all as writing
      for (int i = 0; i < updatedSections.length; i++) {
        updatedSections[i] =
            updatedSections[i].copyWith(status: SectionStatus.writing);
      }
      yield state.copyWith(
        sections: List.from(updatedSections),
        status: GenerationStatus.writing,
      );

      // Step 3: Get full report (server runs workers in parallel internally)
      yield state.copyWith(
        sections: List.from(updatedSections),
        status: GenerationStatus.synthesizing,
      );

      final reportResponse = await http.post(
        Uri.parse('$baseUrl/generate-report'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'topic': topic}),
      );

      if (reportResponse.statusCode != 200) {
        throw Exception('Generation failed: ${reportResponse.body}');
      }

      final reportData =
          jsonDecode(reportResponse.body) as Map<String, dynamic>;
      final finalReport = reportData['final_report'] as String;
      final completedSections =
          (reportData['sections'] as List?)?.map((s) {
            return ReportSection(
              name: s['name'] as String,
              description: s['description'] as String,
              content: s['content'] as String?,
              status: SectionStatus.done,
            );
          }).toList() ??
          updatedSections
              .map((s) => s.copyWith(status: SectionStatus.done))
              .toList();

      yield state.copyWith(
        sections: completedSections,
        finalReport: finalReport,
        status: GenerationStatus.done,
      );
    } catch (e) {
      yield state.copyWith(
        status: GenerationStatus.error,
        errorMessage: e.toString(),
      );
    }
  }
}
