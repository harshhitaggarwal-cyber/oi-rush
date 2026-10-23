import 'package:flutter/material.dart';

void main() => runApp(const OIRushApp());
const ink = Color(0xFF07142B), panel = Color(0xFF102342), mint = Color(0xFF00F5C8), blue = Color(0xFF2F78FF), violet = Color(0xFF8757FF);

class OIRushApp extends StatelessWidget {
  const OIRushApp({super.key});
  @override Widget build(BuildContext context) => MaterialApp(title: 'OI Rush', debugShowCheckedModeBanner: false, theme: ThemeData(brightness: Brightness.dark, scaffoldBackgroundColor: ink, colorScheme: ColorScheme.fromSeed(seedColor: mint, brightness: Brightness.dark), useMaterial3: true), home: const Home());
}

class Home extends StatelessWidget {
  const Home({super.key});
  @override Widget build(BuildContext context) => Scaffold(body: SafeArea(child: ListView(padding: const EdgeInsets.all(22), children: [
    const SizedBox(height: 28), Center(child: Container(width: 84, height: 84, decoration: BoxDecoration(gradient: const LinearGradient(colors: [mint, blue, violet]), borderRadius: BorderRadius.circular(25)), child: const Icon(Icons.bolt_rounded, color: ink, size: 50))),
    const SizedBox(height: 18), const Center(child: Text.rich(TextSpan(style: TextStyle(fontSize: 36, fontWeight: FontWeight.w900), children: [TextSpan(text: 'OI ', style: TextStyle(color: Colors.white)), TextSpan(text: 'Rush', style: TextStyle(color: mint))]))),
    const SizedBox(height: 18), const Text("Let's enter the world of FnO with an EDGE", textAlign: TextAlign.center, style: TextStyle(fontSize: 25, height: 1.2, fontWeight: FontWeight.w800)),
    const SizedBox(height: 10), const Text('One platform. Two markets. Your edge.', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFF9FB2D0))), const SizedBox(height: 34),
    _MarketCard(title: 'NSE', subtitle: 'Indices & Stocks', detail: 'OPTION CHAIN ANALYSIS', color: blue, icon: Icons.candlestick_chart_rounded, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const Analysis(market: 'NSE')))),
    const SizedBox(height: 16), _MarketCard(title: 'MCX', subtitle: 'All Commodity Options', detail: 'GOLD · SILVER · ENERGY · BASE METALS · ALL ACTIVE CONTRACTS', color: violet, icon: Icons.diamond_rounded, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const Analysis(market: 'MCX')))),
    const SizedBox(height: 28), const Center(child: Text('DEMO MODE · NO LIVE MARKET DATA', style: TextStyle(color: Color(0xFF7F91AF), fontSize: 11, letterSpacing: 1.1)))
  ]))));
}

class _MarketCard extends StatelessWidget {
  const _MarketCard({required this.title, required this.subtitle, required this.detail, required this.color, required this.icon, required this.onTap});
  final String title, subtitle, detail; final Color color; final IconData icon; final VoidCallback onTap;
  @override Widget build(BuildContext context) => Material(color: panel, borderRadius: BorderRadius.circular(24), child: InkWell(onTap: onTap, borderRadius: BorderRadius.circular(24), child: Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(borderRadius: BorderRadius.circular(24), border: Border.all(color: color)), child: Row(children: [Container(width: 58, height: 58, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(18)), child: Icon(icon, size: 32, color: Colors.white)), const SizedBox(width: 16), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800)), const SizedBox(height: 4), Text(subtitle, style: const TextStyle(color: Color(0xFFC2D0E5))), const SizedBox(height: 8), Text(detail, style: const TextStyle(color: mint, fontSize: 9, letterSpacing: .5, fontWeight: FontWeight.w700))])), const Icon(Icons.arrow_forward_rounded, color: mint)]))));
}

class Analysis extends StatefulWidget {
  const Analysis({super.key, required this.market}); final String market;
  @override State<Analysis> createState() => _AnalysisState();
}
class _AnalysisState extends State<Analysis> {
  String? underlying; String expiry = 'Select expiry';
  @override Widget build(BuildContext context) {
    final mcx = widget.market == 'MCX'; final instruments = mcx ? ['Select commodity', 'Gold', 'Gold Mini', 'Silver', 'Silver Mini', 'Crude Oil', 'Natural Gas', 'Copper', 'Zinc', 'Aluminium', 'Lead', 'Nickel'] : ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'Select stock'];
    underlying ??= instruments.first;
    const expiries = ['Select expiry', 'Nearest available expiry', 'Next available expiry'];
    return Scaffold(appBar: AppBar(title: Text('OI Rush · ${widget.market}')), body: ListView(padding: const EdgeInsets.all(18), children: [Text(mcx ? 'MCX Commodity Options' : 'NSE Options', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800)), const SizedBox(height: 8), const Text('Selectors are placeholders until an official contract master and authorized data feed are connected.', style: TextStyle(color: Color(0xFF9FB2D0))), const SizedBox(height: 20), DropdownButtonFormField<String>(value: underlying, decoration: const InputDecoration(labelText: 'Underlying / Commodity', border: OutlineInputBorder()), items: instruments.map((x) => DropdownMenuItem(value: x, child: Text(x))).toList(), onChanged: (v) => setState(() => underlying = v)), const SizedBox(height: 14), DropdownButtonFormField<String>(value: expiry, decoration: const InputDecoration(labelText: 'Expiry', border: OutlineInputBorder()), items: expiries.map((x) => DropdownMenuItem(value: x, child: Text(x))).toList(), onChanged: (v) => setState(() => expiry = v ?? expiry)), const SizedBox(height: 20), Container(padding: const EdgeInsets.all(14), decoration: BoxDecoration(color: panel, borderRadius: BorderRadius.circular(16)), child: const Row(children: [Icon(Icons.schedule_rounded, color: mint), SizedBox(width: 10), Expanded(child: Text('Snapshot target: 6:00 PM IST · Exchange calendar required'))])), const SizedBox(height: 20), const Text('OPTION CHAIN · ILLUSTRATIVE ONLY', style: TextStyle(color: mint, fontSize: 12, letterSpacing: 1, fontWeight: FontWeight.w800)), const SizedBox(height: 10), SingleChildScrollView(scrollDirection: Axis.horizontal, child: DataTable(headingRowColor: WidgetStateProperty.all(panel), columns: const [DataColumn(label: Text('Strike')), DataColumn(label: Text('OI PCR')), DataColumn(label: Text('LTP PCR')), DataColumn(label: Text('OI Analysis'))], rows: const [DataRow(cells: [DataCell(Text('25,400')), DataCell(Text('1.24')), DataCell(Text('0.82')), DataCell(Text('Initially Bullish'))]), DataRow(cells: [DataCell(Text('25,450')), DataCell(Text('0.91')), DataCell(Text('1.05')), DataCell(Text('Strong Bullish'))]), DataRow(cells: [DataCell(Text('25,500')), DataCell(Text('0.78')), DataCell(Text('1.17')), DataCell(Text('Neutral / No Setup'))])])), const SizedBox(height: 12), const Text('Sample rows are fictional. No current market data is being shown.', style: TextStyle(color: Color(0xFF9FB2D0), fontSize: 12))]));
  }
}
