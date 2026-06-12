class ReportSection {
  final String name;
  final String description;
  final String? content;
  final SectionStatus status;

  ReportSection({
    required this.name,
    required this.description,
    this.content,
    this.status = SectionStatus.pending,
  });

  ReportSection copyWith({
    String? name,
    String? description,
    String? content,
    SectionStatus? status,
  }) {
    return ReportSection(
      name: name ?? this.name,
      description: description ?? this.description,
      content: content ?? this.content,
      status: status ?? this.status,
    );
  }
}

enum SectionStatus { pending, writing, done, error }

class ReportState {
  final String topic;
  final List<ReportSection> sections;
  final String? finalReport;
  final GenerationStatus status;
  final String? errorMessage;

  ReportState({
    required this.topic,
    this.sections = const [],
    this.finalReport,
    this.status = GenerationStatus.idle,
    this.errorMessage,
  });

  ReportState copyWith({
    String? topic,
    List<ReportSection>? sections,
    String? finalReport,
    GenerationStatus? status,
    String? errorMessage,
  }) {
    return ReportState(
      topic: topic ?? this.topic,
      sections: sections ?? this.sections,
      finalReport: finalReport ?? this.finalReport,
      status: status ?? this.status,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

enum GenerationStatus { idle, planning, writing, synthesizing, done, error }
