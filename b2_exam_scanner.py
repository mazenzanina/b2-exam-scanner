import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// ---------------------------------------------------------------------------
// 1. DATA MODELS
// ---------------------------------------------------------------------------

class Question {
  final int id;
  // In a real app, this would be an asset path 'assets/q1.png'
  final IconData visualPattern; 
  final List<IconData> options;
  final int correctOptionIndex;

  Question({
    required this.id,
    required this.visualPattern,
    required this.options,
    required this.correctOptionIndex,
  });
}

// ---------------------------------------------------------------------------
// 2. MOCK DATA (Replace with real Image Assets)
// ---------------------------------------------------------------------------

final List<Question> demoQuestions = [
  Question(
    id: 1,
    visualPattern: Icons.grid_3x3, // Represents the Matrix puzzle
    options: [Icons.circle, Icons.square, Icons.star, Icons.check_box_outline_blank],
    correctOptionIndex: 1,
  ),
  Question(
    id: 2,
    visualPattern: Icons.apps,
    options: [Icons.filter_1, Icons.filter_2, Icons.filter_3, Icons.filter_4],
    correctOptionIndex: 3,
  ),
  Question(
    id: 3,
    visualPattern: Icons.pie_chart,
    options: [Icons.timelapse, Icons.data_usage, Icons.donut_large, Icons.circle],
    correctOptionIndex: 2,
  ),
  // Add 20-30 more questions here for a real test
];

// ---------------------------------------------------------------------------
// 3. MAIN APP ENTRY
// ---------------------------------------------------------------------------

void main() {
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
  ));
  runApp(const IQTestApp());
}

class IQTestApp extends StatelessWidget {
  const IQTestApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Official IQ Test',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2A2D34), // Dark modern grey
          primary: const Color(0xFF007AFF),   // Trustworthy Blue
          secondary: const Color(0xFF34C759), // Success Green
        ),
        fontFamily: 'Roboto', // Use a clean font like Roboto or Montserrat
        scaffoldBackgroundColor: const Color(0xFFF5F7FA),
      ),
      home: const WelcomeScreen(),
    );
  }
}

// ---------------------------------------------------------------------------
// 4. WELCOME SCREEN
// ---------------------------------------------------------------------------

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Spacer(),
              const Icon(Icons.psychology, size: 100, color: Color(0xFF007AFF)),
              const SizedBox(height: 24),
              const Text(
                "Standardized IQ Test",
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.black87),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              const Text(
                "Based on Raven's Progressive Matrices. \nDiscover your cognitive potential.",
                style: TextStyle(fontSize: 16, color: Colors.black54),
                textAlign: TextAlign.center,
              ),
              const Spacer(),
              _buildFeatureRow(Icons.timer, "20 Minutes"),
              _buildFeatureRow(Icons.question_answer, "30 Questions"),
              _buildFeatureRow(Icons.poll, "Instant Results"),
              const Spacer(),
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: () => Navigator.push(
                    context, 
                    MaterialPageRoute(builder: (context) => const QuizScreen())
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Theme.of(context).primaryColor,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    elevation: 4,
                  ),
                  child: const Text("START TEST", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFeatureRow(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 20, color: Colors.grey),
          const SizedBox(width: 10),
          Text(text, style: const TextStyle(color: Colors.black54, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// 5. QUIZ SCREEN (The Core Logic)
// ---------------------------------------------------------------------------

class QuizScreen extends StatefulWidget {
  const QuizScreen({super.key});

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  int _currentIndex = 0;
  int _score = 0;
  int _timeLeft = 1200; // 20 minutes in seconds
  Timer? _timer;
  
  // Track selected answers
  final Map<int, int> _answers = {};

  @override
  void initState() {
    super.initState();
    _startTimer();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_timeLeft > 0) {
        setState(() => _timeLeft--);
      } else {
        _finishTest();
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _answerQuestion(int optionIndex) {
    setState(() {
      _answers[_currentIndex] = optionIndex;
    });

    // Auto advance after short delay
    Future.delayed(const Duration(milliseconds: 300), () {
      if (_currentIndex < demoQuestions.length - 1) {
        setState(() => _currentIndex++);
      } else {
        _finishTest();
      }
    });
  }

  void _finishTest() {
    _timer?.cancel();
    // Calculate raw score
    _score = 0;
    _answers.forEach((index, answer) {
      if (demoQuestions[index].correctOptionIndex == answer) {
        _score++;
      }
    });

    Navigator.pushReplacement(
      context, 
      MaterialPageRoute(builder: (context) => ResultScreen(rawScore: _score, totalQuestions: demoQuestions.length))
    );
  }

  String get _timerString {
    final minutes = (_timeLeft / 60).floor();
    final seconds = _timeLeft % 60;
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final question = demoQuestions[_currentIndex];
    final progress = (_currentIndex + 1) / demoQuestions.length;

    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text("Q ${_currentIndex + 1} / ${demoQuestions.length}", 
                style: const TextStyle(color: Colors.black87, fontWeight: FontWeight.bold)),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.red.withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Row(
                children: [
                  const Icon(Icons.timer_outlined, color: Colors.red, size: 16),
                  const SizedBox(width: 4),
                  Text(_timerString, style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
                ],
              ),
            )
          ],
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(6),
          child: LinearProgressIndicator(
            value: progress,
            backgroundColor: Colors.grey[300],
            valueColor: AlwaysStoppedAnimation<Color>(Theme.of(context).primaryColor),
          ),
        ),
      ),
      body: Column(
        children: [
          // THE PUZZLE (Matrix)
          Expanded(
            flex: 4,
            child: Container(
              margin: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 5))],
              ),
              child: Center(
                // In a real app, use Image.asset(question.imagePath)
                child: Icon(question.visualPattern, size: 150, color: Colors.black87),
              ),
            ),
          ),
          
          const Text("Select the missing piece:", style: TextStyle(color: Colors.grey, fontSize: 16)),
          const SizedBox(height: 10),

          // THE OPTIONS
          Expanded(
            flex: 3,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: GridView.builder(
                itemCount: question.options.length,
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  childAspectRatio: 2.5,
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                ),
                itemBuilder: (ctx, index) {
                  final isSelected = _answers[_currentIndex] == index;
                  return InkWell(
                    onTap: () => _answerQuestion(index),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      decoration: BoxDecoration(
                        color: isSelected ? Theme.of(context).primaryColor.withOpacity(0.1) : Colors.white,
                        border: Border.all(
                          color: isSelected ? Theme.of(context).primaryColor : Colors.grey.shade300,
                          width: 2
                        ),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Center(
                        child: Icon(question.options[index], 
                          color: isSelected ? Theme.of(context).primaryColor : Colors.black54),
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// 6. RESULT SCREEN
// ---------------------------------------------------------------------------

class ResultScreen extends StatefulWidget {
  final int rawScore;
  final int totalQuestions;

  const ResultScreen({super.key, required this.rawScore, required this.totalQuestions});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  int _calculatedIQ = 0;

  @override
  void initState() {
    super.initState();
    // Simple Gaussian calculation approximation (Mean 100, SD 15)
    // In a real app, use age-normed tables.
    double percentage = widget.rawScore / widget.totalQuestions;
    // This is a dummy formula for visual representation only
    int baseIQ = 70 + (percentage * 70).round(); 
    _calculatedIQ = baseIQ;

    _controller = AnimationController(vsync: this, duration: const Duration(seconds: 2));
    _animation = Tween<double>(begin: 0, end: _calculatedIQ.toDouble()).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut)
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text("TEST COMPLETE", style: TextStyle(letterSpacing: 2, fontWeight: FontWeight.bold, color: Colors.grey)),
              const SizedBox(height: 30),
              Container(
                height: 200,
                width: 200,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: Theme.of(context).primaryColor, width: 8),
                  color: Colors.white,
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text("Your IQ", style: TextStyle(fontSize: 18, color: Colors.grey)),
                      AnimatedBuilder(
                        animation: _animation,
                        builder: (context, child) {
                          return Text(
                            _animation.value.toStringAsFixed(0),
                            style: TextStyle(
                              fontSize: 60, 
                              fontWeight: FontWeight.w900, 
                              color: Theme.of(context).primaryColor
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 40),
              Card(
                elevation: 0,
                color: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      _buildDetailRow("Correct Answers", "${widget.rawScore}/${widget.totalQuestions}"),
                      const Divider(),
                      _buildDetailRow("Percentile", "Top ${100 - ((widget.rawScore/widget.totalQuestions)*100).round()}%"),
                      const Divider(),
                      _buildDetailRow("Classification", _getClassification(_calculatedIQ)),
                    ],
                  ),
                ),
              ),
              const Spacer(),
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: () {
                    // Placeholder for "Get Detailed Report" (In-App Purchase)
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Redirecting to Pro Payment...")));
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF34C759),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: const Text("GET FULL CERTIFICATE", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text("Retake Test", style: TextStyle(color: Colors.grey)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _getClassification(int iq) {
    if (iq >= 130) return "Very Superior";
    if (iq >= 120) return "Superior";
    if (iq >= 110) return "High Average";
    if (iq >= 90) return "Average";
    return "Below Average";
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 16, color: Colors.black54)),
          Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}