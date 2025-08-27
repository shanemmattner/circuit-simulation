# Progressive Exercise Difficulty Mapping
## Scaffolded Learning Path with Bloom's Taxonomy Integration

## Learning Progression Framework

### Difficulty Levels
- **🟢 Level 1**: Remember & Understand (Easy - 90% success rate)
- **🟡 Level 2**: Apply & Analyze (Medium - 70% success rate)  
- **🔴 Level 3**: Evaluate & Create (Hard - 50% success rate)

### Exercise Types by Difficulty

#### 🎯 **TRY Exercises** (30 sec - 1 min) - Level 1
**Goal**: Quick confidence builders, concept verification
**Success Rate Target**: 90%+

#### 🔧 **BUILD Exercises** (3-5 min) - Level 1-2
**Goal**: Guided construction with scaffolding
**Success Rate Target**: 80%+

#### ⚡ **CHALLENGE Exercises** (5-15 min) - Level 2-3
**Goal**: Independent problem-solving
**Success Rate Target**: 60%+ (with hints)

## Complete Learning Path Mapping

## **TRACK 1: DC ANALYSIS FUNDAMENTALS**

### Module 1.1: What is DC Analysis?
**Learning Objective**: Understand DC analysis concept and basic voltage measurement

#### 📚 **Theory**: DC Analysis Introduction (2 min)
```markdown
DC Analysis finds the "steady state" - what happens after everything settles.
Like asking: "What do I measure with a voltmeter after waiting 10 seconds?"
```

#### 🎯 **Try 1.1.1**: Voltage Prediction (30 sec) - 🟢 Level 1
```python
# Simple multiple choice - just getting familiar
"9V battery connected to 1kΩ resistor. Voltage at battery terminal?"
Options: [3V, 6V, 9V, 12V]
Correct: 9V
Success_criteria: Answer correctly on first or second try
```

#### 📚 **Theory**: Voltage vs Current Concept (1 min)
```markdown  
Voltage = "pressure" (exists even without flow)
Current = "flow" (only happens with complete path)
```

#### 🎯 **Try 1.1.2**: Current Calculation (1 min) - 🟢 Level 1  
```python
# Simple Ohm's law application
"Same 9V battery, 1kΩ resistor. What current flows?"
User_input: Slider from 0-50mA  
Correct: 9mA (±0.5mA tolerance)
Instant_feedback: "I = V/R = 9V/1000Ω = 9mA"
```

#### 🔧 **Build 1.1.1**: First Circuit Simulation (3 min) - 🟢 Level 1
```python
# Guided circuit construction with live feedback
"""
Step-by-step builder:
1. "Add a voltage source" → User clicks, gets voltage source
2. "Set it to 5V" → Slider appears, user adjusts
3. "Add a resistor" → User clicks, gets resistor  
4. "Connect them" → Visual connection tool
5. "Run simulation" → Automatic simulation + results

Success: Circuit simulates without errors
Scaffolding: Each step has visual hints, can't proceed until correct
"""
```

### Module 1.2: Voltage Dividers
**Learning Objective**: Design and analyze voltage divider circuits

#### 📚 **Theory**: Voltage Division Concept (2 min)
```markdown
Two resistors in series "divide" the input voltage proportionally.
Like two people sharing pizza - bigger person gets bigger slice.
Formula: V_out = V_in × (R2/(R1+R2))
```

#### 🎯 **Try 1.2.1**: Formula Application (1 min) - 🟢 Level 1
```python
# Straightforward calculation
"5V input, R1=1kΩ, R2=2kΩ. Calculate V_out."
User_input: Number entry with unit
Correct: 3.33V (±0.1V)
Hint_after_1_wrong: "Use the voltage divider formula"
Hint_after_2_wrong: "V_out = 5V × (2000/(1000+2000)) = ?"
```

#### 🔧 **Build 1.2.1**: Interactive Voltage Divider (4 min) - 🟡 Level 2
```python
# Real-time parameter exploration
"""
Interactive sliders:
- V_in: 1V to 12V
- R1: 100Ω to 10kΩ  
- R2: 100Ω to 10kΩ

Live updates:
- Circuit diagram updates
- V_out calculation shows
- Actual simulation runs
- Plot shows voltage at each node

Goal: Create exactly 3.3V output from 5V input
Success: Get within ±0.1V of target
Scaffolding: Real-time hints when getting close/far from target
"""
```

#### ⚡ **Challenge 1.2.1**: 3-Level Battery Monitor (8 min) - 🟡 Level 2
```python
# Multi-constraint optimization problem
"""
Design Challenge: Car Battery Monitor
Requirements:
- Monitor 12V car battery (range: 10V to 14V)
- Output to 3.3V microcontroller ADC
- Three distinct levels: Low (<11V), OK (11-13V), Critical (>13V)
- Use standard resistor values only
- Current draw < 1mA

Success Criteria:
- All voltage ranges map correctly
- Current consumption acceptable  
- Uses only E12 standard resistor values
- Simulation verifies design

Scaffolding:
- Standard resistor value selector
- Real-time current calculation
- Color-coded feedback for each requirement
- Hint system for common mistakes
"""
```

### Module 1.3: Current Limiting and Safety
**Learning Objective**: Design safe current limiting circuits

#### 📚 **Theory**: Current, Power, and Component Safety (3 min)
```markdown
LEDs, motors, and sensors need current limiting or they burn out.
Power = Voltage × Current (P = VI)
Resistors dissipate power as heat - must stay within rating.
Safety first: Always calculate worst-case power dissipation.
```

#### 🎯 **Try 1.3.1**: Power Calculation (1 min) - 🟢 Level 1
```python
# Basic power calculation
"5V across 100Ω resistor. How much power dissipated?"  
Options: [0.05W, 0.25W, 0.5W, 1W]
Correct: 0.25W  
Explanation: "P = V²/R = 5²/100 = 0.25W"
```

#### 🔧 **Build 1.3.1**: LED Current Limiter (4 min) - 🟡 Level 2
```python
# Practical safety-focused design
"""
Interactive LED Calculator:
- LED forward voltage: 1.8V to 3.5V (dropdown for colors)
- Supply voltage: 3V to 12V
- Target current: 10mA to 30mA
- Safety margin: 10% to 50%

Real-time feedback:
- Required resistor value
- Actual current with standard resistor
- Power dissipation in resistor
- LED brightness estimate
- Safety warnings if overcurrent

Success: Design safe LED circuit with <5% current error
Visual: LED brightness changes with current setting
"""
```

#### ⚡ **Challenge 1.3.1**: Multi-LED Array Design (12 min) - 🔴 Level 3
```python
# Complex multi-constraint optimization
"""
Design Challenge: 12V Automotive LED Array
Requirements:
- 8 LEDs total (2.1V forward voltage, 20mA each)
- 12V car electrical system (10V-14V range)
- Minimize power waste
- All LEDs must have similar brightness
- Handle voltage variations gracefully
- Use only standard components

Design Options:
1. All in series (requires voltage boost?)
2. All in parallel (high current?)  
3. Series-parallel combination (optimal?)
4. Current regulator IC (advanced?)

Success Criteria:
- <10% brightness variation between LEDs
- <20% power waste  
- Works across full voltage range
- Passes automotive reliability standards

Advanced Features:
- Monte Carlo analysis with component tolerances
- Temperature coefficient modeling
- Cost optimization (component price database)
"""
```

## **TRACK 2: TRANSIENT ANALYSIS FUNDAMENTALS**

### Module 2.1: Time-Domain Behavior Introduction
**Learning Objective**: Understand what transient analysis reveals

#### 📚 **Theory**: Why Time Matters (2 min)
```markdown
Real circuits don't change instantly - they have "startup time."
Capacitors take time to charge, inductors resist current changes.
Transient analysis shows the "movie" of how your circuit responds over time.
```

#### 🎯 **Try 2.1.1**: Predict Charging Behavior (45 sec) - 🟢 Level 1
```python
# Conceptual understanding check
"RC circuit: 1µF capacitor, 1kΩ resistor, 5V step input"
"What happens to capacitor voltage over time?"

Options with animations:
A) Instant jump to 5V
B) Linear ramp to 5V  
C) Exponential curve to 5V ✓
D) Oscillation around 5V

Correct: C
Visual: Shows actual exponential curve animation
```

#### 🔧 **Build 2.1.1**: RC Charging Explorer (5 min) - 🟡 Level 2
```python
# Parameter exploration with immediate visual feedback
"""
Interactive RC Circuit:
- R slider: 100Ω to 100kΩ (log scale)
- C slider: 1nF to 1mF (log scale)  
- Voltage step: 1V to 10V

Live simulation:
- Time constant τ = RC calculation
- Real transient simulation (0 to 5τ)
- Animated charging curve
- 63.2% point highlighted
- Rise time (10% to 90%) calculation

Goal: Design for specific rise time (user selects target)
Success: Get within ±10% of target rise time
Educational: See relationship between R, C, and timing
"""
```

#### ⚡ **Challenge 2.1.1**: Camera Flash Timing (10 min) - 🔴 Level 3
```python
# Real-world timing circuit design
"""
Design Challenge: Camera Flash Recharge Timer
Requirements:
- Flash capacitor: 1000µF (fixed)
- Recharge from 0V to 300V in <5 seconds
- Visual indicator when ready (LED turns on)
- Battery powered (minimize current drain)
- Temperature stable (-10°C to +50°C)

Constraints:
- Available power: 6V battery
- Charge current must be limited for safety
- LED threshold: 250V (83% of full charge)
- Component tolerances: ±10%

Success Criteria:
- Recharge time < 5 seconds (worst case)
- LED indicates ready state accurately
- Circuit stable across temperature range
- Monte Carlo analysis shows <5% failures

Advanced Modeling:
- Capacitor leakage current
- Temperature effects on components
- Battery voltage droop under load
"""
```

## **TRACK 3: AC ANALYSIS FUNDAMENTALS**

### Module 3.1: Frequency Response Introduction
**Learning Objective**: Understand frequency-dependent behavior

#### 📚 **Theory**: Why Frequency Matters (3 min)
```markdown
Real circuits behave differently at different frequencies.
Audio filters let bass through but block treble (or vice versa).
AC analysis tests your circuit with sine waves at many frequencies.
Result: Bode plot showing gain and phase vs. frequency.
```

#### 🎯 **Try 3.1.1**: Filter Behavior Prediction (1 min) - 🟢 Level 1
```python
# Conceptual filter understanding
"RC low-pass filter: R=1kΩ, C=1µF"
"Which frequencies pass through best?"

Visual frequency spectrum with slider:
User drags to select frequency range
Options: [1-10Hz, 10-100Hz, 100-1kHz, 1kHz-10kHz, >10kHz]
Correct: 100-1kHz (around cutoff frequency)

Instant feedback: Shows actual Bode plot with selected region highlighted
```

#### 🔧 **Build 3.1.1**: Audio Filter Designer (6 min) - 🟡 Level 2
```python
# Interactive filter design with audio feedback
"""
Audio Filter Studio:
- Filter type: Low-pass, High-pass, Band-pass
- Cutoff frequency: 20Hz to 20kHz (audio range)
- Component values: R, C sliders
- Input: Selectable test tones or music sample

Real-time features:
- Bode plot updates as you adjust components
- Audio output (filtered sound plays through speakers)
- Frequency response visualization
- Phase plot (advanced users)

Goal: Design bass filter (100Hz cutoff) or treble filter (2kHz cutoff)
Success: Get within ±10% of target cutoff frequency
Interactive: Hear the actual filtering effect on audio
"""
```

#### ⚡ **Challenge 3.1.1**: Anti-Aliasing Filter (15 min) - 🔴 Level 3
```python
# Professional digital system design
"""
Design Challenge: ADC Anti-Aliasing Filter
Requirements:
- Sample rate: 1kHz (Nyquist frequency = 500Hz)
- Signal bandwidth: DC to 400Hz (preserve)
- Alias rejection: >60dB at >600Hz (prevent)
- Input impedance: >10kΩ (don't load signal source)
- Output impedance: <100Ω (drive ADC)
- Phase distortion: <10° in passband

Design Constraints:
- 2-pole Butterworth or Chebyshev filter
- Standard capacitor values (E12 series)
- Op-amp available (specify gain-bandwidth)
- Cost target: <$5 in components

Success Criteria:
- Meets all frequency response requirements
- Stability analysis shows stable operation
- Monte Carlo shows <1% failure rate
- Passes EMC susceptibility requirements

Advanced Analysis:
- Group delay distortion
- THD at maximum signal level  
- Temperature coefficient analysis
- Component aging effects (10 year drift)
"""
```

## Assessment and Progression Mechanics

### Mastery Thresholds
```python
MASTERY_LEVELS = {
    'try_exercises': {
        'attempts_allowed': 3,
        'success_threshold': 0.8,  # 80% correct
        'time_bonus': True  # Bonus for quick answers
    },
    'build_exercises': {
        'completion_required': True,
        'accuracy_threshold': 0.9,  # Within 10% of target
        'help_penalty': 0.1  # 10% reduction for using hints
    },
    'challenge_exercises': {
        'completion_required': True,
        'creativity_bonus': True,  # Multiple valid solutions
        'efficiency_scoring': True,  # Reward optimal designs
        'peer_review': True  # Other users can vote on solutions
    }
}
```

### Adaptive Difficulty Algorithm
```python
def adjust_exercise_difficulty(user_history):
    """Dynamically adjust difficulty based on performance"""
    
    recent_performance = user_history[-10:]  # Last 10 exercises
    success_rate = sum(ex['success'] for ex in recent_performance) / len(recent_performance)
    avg_attempts = sum(ex['attempts'] for ex in recent_performance) / len(recent_performance)
    
    if success_rate > 0.9 and avg_attempts < 1.5:
        return "increase_difficulty"  # Too easy, challenge more
    elif success_rate < 0.6 or avg_attempts > 3:
        return "decrease_difficulty"  # Too hard, provide more support
    else:
        return "maintain_difficulty"  # Just right
```

### Progress Visualization
```python
def create_skill_tree():
    """Visual skill progression tree"""
    
    skills = {
        'DC Analysis': {
            'prerequisites': [],
            'unlocks': ['Transient Analysis', 'Power Electronics']
        },
        'Transient Analysis': {
            'prerequisites': ['DC Analysis'],
            'unlocks': ['Control Systems', 'Switching Circuits']
        },
        'AC Analysis': {
            'prerequisites': ['DC Analysis'],  
            'unlocks': ['RF Design', 'Audio Electronics']
        },
        'Filter Design': {
            'prerequisites': ['AC Analysis'],
            'unlocks': ['Signal Processing', 'Communications']
        }
    }
    
    # Interactive skill tree visualization
    # Unlocked skills: Green, Available: Yellow, Locked: Gray
```

This progressive mapping ensures each learner builds genuine competency through hands-on practice before advancing to more complex concepts.