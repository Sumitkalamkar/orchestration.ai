import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/report_service.dart';
import '../models/report_model.dart';
import 'report_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();
  bool _isLoading = false;

  final List<String> _suggestions = [
    'Agentic AI and RAG Systems',
    'The Future of Quantum Computing',
    'Transformer Architecture in NLP',
    'Reinforcement Learning from Human Feedback',
    'Multimodal Foundation Models',
  ];

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _startGeneration() async {
    final topic = _controller.text.trim();
    if (topic.isEmpty) return;

    setState(() => _isLoading = true);

    final stream = ReportService.generateReport(topic);

    if (!mounted) return;

    Navigator.push(
      context,
      PageRouteBuilder(
        pageBuilder: (_, animation, __) => ReportScreen(
          topic: topic,
          reportStream: stream,
        ),
        transitionsBuilder: (_, animation, __, child) {
          return FadeTransition(
            opacity: animation,
            child: SlideTransition(
              position:
                  Tween<Offset>(begin: const Offset(0, 0.05), end: Offset.zero)
                      .animate(CurvedAnimation(
                          parent: animation, curve: Curves.easeOut)),
              child: child,
            ),
          );
        },
        transitionDuration: const Duration(milliseconds: 400),
      ),
    ).then((_) => setState(() => _isLoading = false));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              _buildHeader(),
              const SizedBox(height: 56),

              // Input card
              _buildInputCard(),
              const SizedBox(height: 32),

              // Suggestions
              _buildSuggestions(),
              const SizedBox(height: 40),

              // How it works
              _buildHowItWorks(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF6C63FF), Color(0xFF00D4AA)],
                ),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.auto_awesome, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 10),
            Text(
              'OrchestrAI',
              style: GoogleFonts.spaceMono(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.white70,
                letterSpacing: 1.2,
              ),
            ),
          ],
        ).animate().fadeIn(duration: 400.ms),
        const SizedBox(height: 32),
        Text(
          'Generate\ndeep reports\ninstantly.',
          style: GoogleFonts.inter(
            fontSize: 40,
            fontWeight: FontWeight.w800,
            height: 1.15,
            color: Colors.white,
            letterSpacing: -1,
          ),
        ).animate().fadeIn(duration: 500.ms, delay: 100.ms).slideY(begin: 0.1),
        const SizedBox(height: 16),
        Text(
          'Powered by LangGraph orchestration — plans sections,\nwrites in parallel, synthesizes into a full report.',
          style: GoogleFonts.inter(
            fontSize: 14,
            color: Colors.white38,
            height: 1.6,
          ),
        ).animate().fadeIn(duration: 500.ms, delay: 200.ms),
      ],
    );
  }

  Widget _buildInputCard() {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A24),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFF2A2A3A), width: 1.5),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'REPORT TOPIC',
            style: GoogleFonts.spaceMono(
              fontSize: 11,
              color: const Color(0xFF6C63FF),
              letterSpacing: 1.5,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _controller,
            focusNode: _focusNode,
            style: GoogleFonts.inter(
              fontSize: 16,
              color: Colors.white,
              height: 1.5,
            ),
            maxLines: 3,
            minLines: 2,
            decoration: InputDecoration(
              hintText:
                  'e.g. "The impact of LLMs on scientific research"',
              hintStyle: GoogleFonts.inter(
                color: Colors.white24,
                fontSize: 15,
              ),
              fillColor: const Color(0xFF13131D),
              contentPadding: const EdgeInsets.all(16),
            ),
            onSubmitted: (_) => _startGeneration(),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _startGeneration,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF6C63FF),
                foregroundColor: Colors.white,
                disabledBackgroundColor: const Color(0xFF3A3A5A),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
                elevation: 0,
              ),
              child: _isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white54,
                      ),
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.bolt, size: 18),
                        const SizedBox(width: 8),
                        Text(
                          'Generate Report',
                          style: GoogleFonts.inter(
                            fontWeight: FontWeight.w600,
                            fontSize: 15,
                          ),
                        ),
                      ],
                    ),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 500.ms, delay: 300.ms).slideY(begin: 0.05);
  }

  Widget _buildSuggestions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'TRY THESE',
          style: GoogleFonts.spaceMono(
            fontSize: 10,
            color: Colors.white24,
            letterSpacing: 1.5,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _suggestions.asMap().entries.map((entry) {
            return GestureDetector(
              onTap: () {
                _controller.text = entry.value;
                _controller.selection = TextSelection.fromPosition(
                  TextPosition(offset: entry.value.length),
                );
              },
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1A24),
                  borderRadius: BorderRadius.circular(100),
                  border: Border.all(color: const Color(0xFF2A2A3A)),
                ),
                child: Text(
                  entry.value,
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    color: Colors.white54,
                  ),
                ),
              ),
            )
                .animate(delay: (400 + entry.key * 60).ms)
                .fadeIn()
                .slideX(begin: 0.1);
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildHowItWorks() {
    final steps = [
      (Icons.account_tree_outlined, 'Orchestrator', 'Plans the report structure into focused sections'),
      (Icons.people_outline, 'Parallel Workers', 'Each section is written simultaneously by an LLM worker'),
      (Icons.merge_type, 'Synthesizer', 'Combines all sections into a cohesive final report'),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'HOW IT WORKS',
          style: GoogleFonts.spaceMono(
            fontSize: 10,
            color: Colors.white24,
            letterSpacing: 1.5,
          ),
        ),
        const SizedBox(height: 16),
        ...steps.asMap().entries.map((entry) {
          final (icon, title, desc) = entry.value;
          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: const Color(0xFF1A1A24),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFF2A2A3A)),
                  ),
                  child: Icon(icon, color: const Color(0xFF6C63FF), size: 18),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        desc,
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: Colors.white38,
                          height: 1.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ).animate(delay: (600 + entry.key * 80).ms).fadeIn().slideX(begin: -0.05);
        }),
      ],
    );
  }
}
