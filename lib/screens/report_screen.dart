import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/report_model.dart';

class ReportScreen extends StatefulWidget {
  final String topic;
  final Stream<ReportState> reportStream;

  const ReportScreen({
    super.key,
    required this.topic,
    required this.reportStream,
  });

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen> {
  ReportState? _state;
  bool _showReport = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: StreamBuilder<ReportState>(
        stream: widget.reportStream,
        builder: (context, snapshot) {
          if (snapshot.hasData) {
            _state = snapshot.data;
          }

          final state = _state;

          return Stack(
            children: [
              // Background gradient orb
              Positioned(
                top: -100,
                right: -100,
                child: Container(
                  width: 400,
                  height: 400,
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: RadialGradient(
                      colors: [Color(0x1A6C63FF), Colors.transparent],
                    ),
                  ),
                ),
              ),

              SafeArea(
                child: Column(
                  children: [
                    _buildAppBar(state),
                    Expanded(
                      child: state == null
                          ? _buildInitialLoading()
                          : _buildContent(state),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildAppBar(ReportState? state) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          IconButton(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back_ios_new, size: 18),
            style: IconButton.styleFrom(
              backgroundColor: const Color(0xFF1A1A24),
              foregroundColor: Colors.white70,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.topic,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                if (state != null)
                  Text(
                    _statusLabel(state.status),
                    style: GoogleFonts.spaceMono(
                      fontSize: 10,
                      color: _statusColor(state.status),
                      letterSpacing: 0.5,
                    ),
                  ),
              ],
            ),
          ),
          if (state?.status == GenerationStatus.done) ...[
            IconButton(
              onPressed: _copyReport,
              icon: const Icon(Icons.copy_outlined, size: 18),
              style: IconButton.styleFrom(
                backgroundColor: const Color(0xFF1A1A24),
                foregroundColor: Colors.white70,
              ),
              tooltip: 'Copy report',
            ),
            const SizedBox(width: 8),
            TextButton.icon(
              onPressed: () => setState(() => _showReport = !_showReport),
              icon: Icon(
                _showReport ? Icons.list : Icons.article_outlined,
                size: 16,
              ),
              label: Text(_showReport ? 'Sections' : 'Report'),
              style: TextButton.styleFrom(
                foregroundColor: const Color(0xFF6C63FF),
                textStyle: GoogleFonts.inter(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInitialLoading() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const SizedBox(
            width: 48,
            height: 48,
            child: CircularProgressIndicator(
              color: Color(0xFF6C63FF),
              strokeWidth: 2,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Connecting to orchestrator...',
            style: GoogleFonts.inter(color: Colors.white38, fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _buildContent(ReportState state) {
    if (state.status == GenerationStatus.error) {
      return _buildError(state.errorMessage ?? 'Unknown error');
    }

    if (state.status == GenerationStatus.done && _showReport) {
      return _buildFinalReport(state.finalReport ?? '');
    }

    return _buildProgress(state);
  }

  Widget _buildProgress(ReportState state) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Status banner
          _buildStatusBanner(state),
          const SizedBox(height: 28),

          // Section cards
          if (state.sections.isNotEmpty) ...[
            Text(
              'REPORT SECTIONS',
              style: GoogleFonts.spaceMono(
                fontSize: 10,
                color: Colors.white24,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 14),
            ...state.sections.asMap().entries.map((entry) {
              return _buildSectionCard(entry.value, entry.key)
                  .animate(delay: (entry.key * 80).ms)
                  .fadeIn()
                  .slideX(begin: 0.05);
            }),
          ],

          // Done CTA
          if (state.status == GenerationStatus.done) ...[
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: () => setState(() => _showReport = true),
                icon: const Icon(Icons.article_outlined, size: 18),
                label: Text(
                  'Read Full Report',
                  style: GoogleFonts.inter(
                    fontWeight: FontWeight.w600,
                    fontSize: 15,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6C63FF),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                  elevation: 0,
                ),
              ),
            ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.1),
          ],
        ],
      ),
    );
  }

  Widget _buildStatusBanner(ReportState state) {
    final (icon, message, color) = switch (state.status) {
      GenerationStatus.planning => (
          Icons.account_tree_outlined,
          'Orchestrator is planning report sections...',
          const Color(0xFFFFB347),
        ),
      GenerationStatus.writing => (
          Icons.edit_outlined,
          'Workers writing ${state.sections.length} sections in parallel...',
          const Color(0xFF6C63FF),
        ),
      GenerationStatus.synthesizing => (
          Icons.merge_type,
          'Synthesizer combining sections...',
          const Color(0xFF00D4AA),
        ),
      GenerationStatus.done => (
          Icons.check_circle_outline,
          'Report complete — ${state.sections.length} sections generated.',
          const Color(0xFF00D4AA),
        ),
      _ => (Icons.hourglass_empty, 'Starting...', Colors.white38),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withOpacity(0.25)),
      ),
      child: Row(
        children: [
          state.status != GenerationStatus.done
              ? SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                    color: color,
                    strokeWidth: 2,
                  ),
                )
              : Icon(icon, color: color, size: 18),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: GoogleFonts.inter(
                fontSize: 13,
                color: color,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionCard(ReportSection section, int index) {
    final statusColor = switch (section.status) {
      SectionStatus.pending => Colors.white24,
      SectionStatus.writing => const Color(0xFF6C63FF),
      SectionStatus.done => const Color(0xFF00D4AA),
      SectionStatus.error => Colors.redAccent,
    };

    final statusIcon = switch (section.status) {
      SectionStatus.pending => Icons.radio_button_unchecked,
      SectionStatus.writing => Icons.pending_outlined,
      SectionStatus.done => Icons.check_circle_outline,
      SectionStatus.error => Icons.error_outline,
    };

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A24),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: statusColor.withOpacity(0.3),
          width: 1.5,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Status icon
          Padding(
            padding: const EdgeInsets.only(top: 2),
            child: section.status == SectionStatus.writing
                ? SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      color: statusColor,
                      strokeWidth: 2,
                    ),
                  )
                : Icon(statusIcon, color: statusColor, size: 16),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  section.name,
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  section.description,
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    color: Colors.white38,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
          // Section number badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: const Color(0xFF13131D),
              borderRadius: BorderRadius.circular(100),
            ),
            child: Text(
              '${index + 1}',
              style: GoogleFonts.spaceMono(
                fontSize: 10,
                color: Colors.white24,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFinalReport(String report) {
    return Column(
      children: [
        Expanded(
          child: Markdown(
            data: report,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            styleSheet: MarkdownStyleSheet(
              h1: GoogleFonts.inter(
                fontSize: 26,
                fontWeight: FontWeight.w800,
                color: Colors.white,
                height: 1.3,
              ),
              h2: GoogleFonts.inter(
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: Colors.white,
                height: 1.4,
              ),
              h3: GoogleFonts.inter(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
              p: GoogleFonts.inter(
                fontSize: 14,
                color: Colors.white70,
                height: 1.8,
              ),
              strong: GoogleFonts.inter(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
              code: GoogleFonts.spaceMono(
                fontSize: 13,
                color: const Color(0xFF00D4AA),
                backgroundColor: const Color(0xFF1A1A24),
              ),
              codeblockDecoration: BoxDecoration(
                color: const Color(0xFF1A1A24),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF2A2A3A)),
              ),
              blockquoteDecoration: const BoxDecoration(
                border: Border(
                  left: BorderSide(color: Color(0xFF6C63FF), width: 3),
                ),
                color: Color(0x0D6C63FF),
              ),
              blockquote: GoogleFonts.inter(
                fontSize: 14,
                color: Colors.white54,
                fontStyle: FontStyle.italic,
              ),
              listBullet: GoogleFonts.inter(
                fontSize: 14,
                color: const Color(0xFF6C63FF),
              ),
              horizontalRuleDecoration: const BoxDecoration(
                border: Border(
                  bottom: BorderSide(color: Color(0xFF2A2A3A), width: 1),
                ),
              ),
            ),
          ),
        ),
        _buildCopyBar(),
      ],
    );
  }

  Widget _buildCopyBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      decoration: const BoxDecoration(
        color: Color(0xFF0F0F14),
        border: Border(top: BorderSide(color: Color(0xFF2A2A3A))),
      ),
      child: Row(
        children: [
          Text(
            '${_state?.sections.length ?? 0} sections · ${_wordCount(_state?.finalReport ?? '')} words',
            style: GoogleFonts.spaceMono(
              fontSize: 11,
              color: Colors.white24,
            ),
          ),
          const Spacer(),
          OutlinedButton.icon(
            onPressed: _copyReport,
            icon: const Icon(Icons.copy_outlined, size: 14),
            label: const Text('Copy Markdown'),
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.white54,
              side: const BorderSide(color: Color(0xFF2A2A3A)),
              textStyle: GoogleFonts.inter(fontSize: 12),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildError(String message) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: Colors.redAccent, size: 48),
            const SizedBox(height: 16),
            Text(
              'Generation Failed',
              style: GoogleFonts.inter(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              message,
              style: GoogleFonts.inter(
                fontSize: 13,
                color: Colors.white38,
                height: 1.6,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Make sure your FastAPI backend is running on localhost:8000',
              style: GoogleFonts.inter(
                fontSize: 12,
                color: Colors.white24,
                fontStyle: FontStyle.italic,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            OutlinedButton(
              onPressed: () => Navigator.pop(context),
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFF6C63FF),
                side: const BorderSide(color: Color(0xFF6C63FF)),
              ),
              child: const Text('Go Back'),
            ),
          ],
        ),
      ),
    );
  }

  void _copyReport() {
    if (_state?.finalReport != null) {
      Clipboard.setData(ClipboardData(text: _state!.finalReport!));
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Report copied to clipboard',
            style: GoogleFonts.inter(fontSize: 13),
          ),
          backgroundColor: const Color(0xFF1A1A24),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  String _statusLabel(GenerationStatus status) {
    return switch (status) {
      GenerationStatus.idle => 'IDLE',
      GenerationStatus.planning => 'PLANNING...',
      GenerationStatus.writing => 'WRITING...',
      GenerationStatus.synthesizing => 'SYNTHESIZING...',
      GenerationStatus.done => 'COMPLETE',
      GenerationStatus.error => 'ERROR',
    };
  }

  Color _statusColor(GenerationStatus status) {
    return switch (status) {
      GenerationStatus.done => const Color(0xFF00D4AA),
      GenerationStatus.error => Colors.redAccent,
      GenerationStatus.planning => const Color(0xFFFFB347),
      _ => const Color(0xFF6C63FF),
    };
  }

  int _wordCount(String text) {
    if (text.isEmpty) return 0;
    return text.trim().split(RegExp(r'\s+')).length;
  }
}
