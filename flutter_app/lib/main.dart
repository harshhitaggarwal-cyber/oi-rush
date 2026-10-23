import 'package:flutter/material.dart';

void main() => runApp(const OIRushApp());
const ink = Color(0xFF07142B), panel = Color(0xFF102342), mint = Color(0xFF00F5C8), blue = Color(0xFF2F78FF);

class OIRushApp extends StatelessWidget {
  const OIRushApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'OI Rush',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(brightness: Brightness.dark, scaffoldBackgroundColor: ink, colorScheme: ColorScheme.fromSeed(seedColor: mint, brightness: Brightness.dark), useMaterial3: true),
    home: const Home(),
  );
}

class Home extends StatelessWidget {
  const Home({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(child: ListView(padding: const EdgeInsets.all(22), children: [
      const SizedBox(height: 28),
      Center(child: Container(width: 84, height: 84, decoration: BoxDecoration(gradient: const LinearGradient(colors: [mint, blue]), borderRadius: BorderRadius.circular(25)), child: const Icon(Icons.bolt_rounded, color: ink, size: 50))),
      const SizedBox(height: 18),
      const Center(child: Text.rich(TextSpan(style: TextStyle(fontSize: 36, fontWeight: FontWeight.w900), children: [TextSpan(text: 'OI ', style: TextStyle(color: Colors.white)), TextSpan(text: 'Rush', style: TextStyle(color: mint))]))),
      const SizedBox(height: 18),
      const Text("Let's enter the world of FnO with an EDGE", textAlign: TextAlign.center, style: TextStyle(fontSize: 25, height: 1.2, fontWeight: FontWeight.w800)),
      const SizedBox(height: 10),
      const Text('NSE options. Clearer analysis.', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFF9FB2D0))),
      const SizedBox(height: 34),
      _MarketCard(title: 'NSE', subtitle: 'Indices & Stocks', detail: 'OPTION CHAIN ANALYSIS', color: blue, icon: Icons.candlestick_chart_rounded, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const Analysis()))),
      const SizedBox(height: 28),
      const Center(child: Text('NSE ONLY · LIVE DATA NOT CONNECTED', style: TextStyle(color: Color(0xFF7F91AF), fontSize: 11, letterSpacing: 1.1))),
    ])),
  );
}

class _MarketCard extends StatelessWidget {
  const _MarketCard({required this.title, required this.subtitle, required this.detail, required this.color, required this.icon, required this.onTap});
  final String title, subtitle, detail; final Color color; final IconData icon; final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => Material(color: panel, borderRadius: BorderRadius.circular(24), child: InkWell(onTap: onTap, borderRadius: BorderRadius.circular(24), child: Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(borderRadius: BorderRadius.circular(24), border: Border.all(color: color)), child: Row(children: [Container(width: 58, height: 58, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(18)), child: Icon(icon, size: 32, color: Colors.white)), const SizedBox(width: 16), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800)), const SizedBox(height: 4), Text(subtitle, style: const TextStyle(color: Color(0xFFC2D0E5))), const SizedBox(height: 8), Text(detail, style: const TextStyle(color: mint, fontSize: 9, letterSpacing: .5, fontWeight: FontWeight.w700))])), const Icon(Icons.arrow_forward_rounded, color: mint)]))));
}

class Analysis extends StatefulWidget {
  const Analysis({super.key});
  @override State<Analysis> createState() => _AnalysisState();
}

class _AnalysisState extends State<Analysis> {
  String? underlying = 'NIFTY';
  String expiry = 'Select expiry';
  final instruments = const ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'Select stock'];
  final expiries = const ['Select expiry', 'Nearest available expiry', 'Next available expiry'];

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('OI Rush · NSE')),
    body: ListView(padding: const EdgeInsets.all(18), children: [
      const Text('NSE Options', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
      const SizedBox(height: 8),
      const Text('Instrument and expiry selectors will use the official contract master when a permitted data feed is connected.', style: TextStyle(color: Color(0xFF9FB2D0))),
      const SizedBox(height: 20),
      DropdownButtonFormField<String>(value: underlying, decoration: const InputDecoration(labelText: 'Underlying / Stock', border: OutlineInputBorder()), items: instruments.map((x) => DropdownMenuItem(value: x, child: Text(x))).toList(), onChanged: (v) => setState(() => underlying = v)),
      const SizedBox(height: 14),
      DropdownButtonFormField<String>(value: expiry, decoration: const InputDecoration(labelText: 'Expiry', border: OutlineInputBorder()), items: expiries.map((x) => DropdownMenuItem(value: x, child: Text(x))).toList(), onChanged: (v) => setState(() => expiry = v ?? expiry)),
      const SizedBox(height: 20),
      Container(padding: const EdgeInsets.all(14), decoration: BoxDecoration(color: panel, borderRadius: BorderRadius.circular(16)), child: const Row(children: [Icon(Icons.schedule_rounded, color: mint), SizedBox(width: 10), Expanded(child: Text('Snapshot target: 6:00 PM IST · NSE F&O calendar required'))])),
      const SizedBox(height: 20),
      Container(padding: const EdgeInsets.all(18), decoration: BoxDecoration(color: panel, borderRadius: BorderRadius.circular(18), border: Border.all(color: const Color(0xFF29415F))), child: const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Icon(Icons.cloud_off_rounded, color: mint, size: 30),
        SizedBox(height: 12),
        Text('Market data unavailable', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
        SizedBox(height: 8),
        Text('A live, authorized NSE data source is not connected yet. No option-chain values or OI signals are displayed until a valid snapshot is available.', style: TextStyle(color: Color(0xFF9FB2D0), height: 1.4)),
      ])),
    ]),
  );
}
