"""
data/experiments.py
────────────────────────────────────────────────────────────────
Complete curriculum dataset for the Virtual Chemistry Lab.
Each experiment contains: name, aim, theory, apparatus,
chemicals, steps, safety instructions, and simulation config.
"""

from data.experiment_loader import load_json_experiments

EXPERIMENTS = {
    8: [
        {
            "id": "c8_e1",
            "name": "Separation of Mixtures",
            "aim": "To separate a mixture of sand and common salt using filtration and evaporation.",
            "theory": (
                "A mixture is a combination of two or more substances that are not chemically combined. "
                "Physical methods can separate mixtures based on differences in physical properties. "
                "Filtration uses a porous filter to remove insoluble solids from a liquid. "
                "Evaporation removes the liquid (solvent) to recover the dissolved solid (solute)."
            ),
            "apparatus": [
                "250 mL Beaker",
                "Glass Funnel",
                "Filter Paper",
                "Glass Rod",
                "Evaporating Dish",
                "Bunsen Burner",
                "Tripod Stand",
                "Wire Gauze",
            ],
            "chemicals": [
                "Sand (insoluble impurity)",
                "Common Salt (NaCl)",
                "Distilled Water (solvent)",
            ],
            "steps": [
                "Dissolve the sand-salt mixture in 100 mL of distilled water in a beaker.",
                "Fold the filter paper into a cone and place it in the funnel.",
                "Pour the mixture slowly through the filter funnel into a clean beaker.",
                "Sand remains on the filter paper; salt solution (filtrate) collects below.",
                "Transfer the filtrate into an evaporating dish.",
                "Heat the evaporating dish gently on the Bunsen burner.",
                "Continue heating until all water evaporates and white salt crystals appear.",
                "Allow the dish to cool; observe and record the recovered salt.",
            ],
            "safety": [
                "Handle the Bunsen burner with care; keep flammables away.",
                "Use tongs when handling the hot evaporating dish.",
                "Do not inhale steam during evaporation.",
                "Wear safety goggles throughout the experiment.",
            ],
            "simulation": {
                "tools": ["BEAKER", "BUNSEN", "DROPPER_WATER"],
                "prefill": {"WATER": 60},
                "reactions": ["evaporation"],
                "theme_color": "#00C8FF",
            },
        },
        {
            "id": "c8_e2",
            "name": "Magnetic Separation",
            "aim": "To separate a mixture of iron filings and sulphur powder using a magnet.",
            "theory": (
                "Magnetic separation exploits the fact that iron is magnetic while sulphur is not. "
                "When a magnet is moved through the mixture, iron filings are attracted to the magnet "
                "and are physically pulled away from the sulphur powder. This is a purely physical "
                "separation — no chemical reaction occurs."
            ),
            "apparatus": [
                "Bar Magnet",
                "Petri Dish (×2)",
                "Spatula",
                "Plain White Paper Sheet",
                "Stirring Rod",
            ],
            "chemicals": [
                "Iron filings (Fe)",
                "Sulphur powder (S)",
            ],
            "steps": [
                "Take equal masses of iron filings and sulphur powder in a petri dish.",
                "Mix them thoroughly with a spatula — observe the mixture closely.",
                "Wrap the bar magnet loosely in a thin plastic sheet.",
                "Slowly move the wrapped magnet over the surface of the mixture.",
                "Iron filings will cling to the magnet; sulphur will remain behind.",
                "Collect the iron filings on a separate sheet of paper by removing the magnet.",
                "Repeat until the sulphur is free of iron filings.",
                "Record observations and weigh each component recovered.",
            ],
            "safety": [
                "Keep magnets away from electronic devices and credit cards.",
                "Sulphur powder can irritate eyes — avoid contact.",
                "Wear gloves when handling iron filings as they may cut skin.",
                "Work on a clean, dry surface.",
            ],
            "simulation": {
                "tools": ["BEAKER"],
                "prefill": {"WATER": 30},
                "reactions": [],
                "theme_color": "#FF8C42",
            },
        },
    ],

    9: [
        {
            "id": "c9_e1",
            "name": "Neutralization of Acid and Base",
            "aim": "To demonstrate the neutralization of an acid by a base using phenolphthalein indicator.",
            "theory": (
                "When an acid reacts with a base, a neutralization reaction takes place to form salt and water. "
                "Phenolphthalein is pink in a basic solution and becomes colourless when the solution turns neutral or acidic. "
                "In this experiment, sodium hydroxide solution is neutralized by dilute hydrochloric acid. "
                "The reaction is: HCl + NaOH → NaCl + H₂O."
            ),
            "apparatus": [
                "Conical Flask (250 mL)",
                "Beaker (100 mL)",
                "Dropper",
                "Measuring Cylinder (25 mL)",
                "Glass Rod",
                "White Tile",
            ],
            "chemicals": [
                "Dilute Hydrochloric Acid (HCl)",
                "Sodium Hydroxide Solution (NaOH)",
                "Phenolphthalein Indicator",
                "Distilled Water",
            ],
            "steps": [
                "Take about 20 mL of sodium hydroxide solution in a conical flask.",
                "Add 2 to 3 drops of phenolphthalein indicator to the flask.",
                "Observe that the basic solution turns pink.",
                "Take dilute hydrochloric acid in a dropper or beaker.",
                "Add the acid slowly to the pink solution while swirling the flask.",
                "Notice the pink colour fading as neutralization proceeds.",
                "Stop when the solution becomes permanently colourless.",
                "Record that acid and base have neutralized to form salt and water.",
            ],
            "safety": [
                "Hydrochloric acid is corrosive — avoid contact with skin and eyes.",
                "Sodium hydroxide is caustic — handle carefully and rinse spills with plenty of water.",
                "Do not taste or directly smell any chemical.",
                "Wear safety goggles and wash hands after the experiment.",
            ],
            "simulation": {
                "tools": ["CONICAL", "BEAKER", "DROPPER_ACID", "DROPPER_BASE", "DROPPER_INDICATOR"],
                "prefill": {"BASE": 50, "ACID": 40, "INDICATOR": 10},
                "reactions": ["acid_base", "neutralization", "color_change"],
                "theme_color": "#38BDF8",
            },
        },
        {
            "id": "c9_e2",
            "name": "pH of Common Solutions",
            "aim": "To determine the pH of common household liquids using universal indicator.",
            "theory": (
                "The pH scale (0–14) measures how acidic or basic a solution is. "
                "A pH below 7 is acidic, exactly 7 is neutral, and above 7 is basic (alkaline). "
                "Universal indicator is a mixture of several indicators that shows a range of colours "
                "corresponding to different pH values, from red (strongly acidic) to violet (strongly basic)."
            ),
            "apparatus": [
                "Test Tubes (×8) with rack",
                "Measuring Cylinder (10 mL)",
                "Dropper",
                "White Tile",
                "pH Colour Chart",
                "Labels / Marker",
            ],
            "chemicals": [
                "Universal Indicator Solution",
                "Lemon Juice (acid)",
                "Vinegar (CH₃COOH)",
                "Distilled Water (neutral)",
                "Milk",
                "Soap Solution (base)",
                "Baking Soda Solution (NaHCO₃)",
                "Bleach Solution (NaOCl)",
            ],
            "steps": [
                "Label 8 test tubes with the names of each solution to be tested.",
                "Pour 5 mL of each solution into its corresponding test tube.",
                "Add 3 drops of universal indicator to each test tube.",
                "Swirl each test tube gently to mix the indicator.",
                "Hold each test tube against the white tile for better colour observation.",
                "Compare the resulting colour with the pH colour chart provided.",
                "Record the approximate pH value for each solution.",
                "Arrange the solutions from most acidic to most basic in a table.",
            ],
            "safety": [
                "Bleach is corrosive — handle with gloves, avoid skin contact.",
                "Do not mix bleach with any acid — toxic gas may form.",
                "Dispose of chemicals in designated waste containers.",
                "Wash hands thoroughly after the experiment.",
            ],
            "simulation": {
                "tools": ["BEAKER", "DROPPER_ACID", "DROPPER_WATER"],
                "prefill": {"ACID": 40, "BASE": 40},
                "reactions": ["acid_base", "neutralization"],
                "theme_color": "#FF6B9D",
            },
        },
    ],

    10: [
        {
            "id": "c10_e1",
            "name": "Electrolysis of Water",
            "aim": "To demonstrate the electrolysis of water and collect hydrogen and oxygen gases.",
            "theory": (
                "Electrolysis is the process of using electrical energy to drive a non-spontaneous "
                "chemical reaction. When electric current passes through acidified water, water molecules "
                "decompose into hydrogen (at the cathode) and oxygen (at the anode). "
                "The reaction is: 2H₂O → 2H₂ + O₂. The volume ratio of H₂ to O₂ is 2:1."
            ),
            "apparatus": [
                "Hoffman Voltameter (or improvised electrolytic cell)",
                "DC Power Supply (6–12 V)",
                "Carbon/Platinum Electrodes (×2)",
                "Connecting Wires with Crocodile Clips",
                "Test Tubes (×2)",
                "Measuring Cylinder",
                "Wooden Splint",
                "Glowing Splint",
            ],
            "chemicals": [
                "Distilled Water",
                "Dilute Sulphuric Acid (H₂SO₄, electrolyte)",
            ],
            "steps": [
                "Fill the electrolytic cell with dilute H₂SO₄ solution.",
                "Fill both inverted test tubes completely with the solution.",
                "Connect the electrodes to the DC power supply (+ve to anode, −ve to cathode).",
                "Switch on the power supply at 6V and observe gas bubbles forming.",
                "Gas collects at cathode (2× volume) and anode (1× volume).",
                "After sufficient gas collects, test cathode gas with a burning splint.",
                "A squeaky pop confirms hydrogen at the cathode.",
                "Test anode gas with a glowing splint — it relights, confirming oxygen.",
            ],
            "safety": [
                "Hydrogen is highly flammable — ensure no sparks near collection tubes.",
                "Dilute H₂SO₄ is corrosive — wear goggles and gloves.",
                "Ensure all electrical connections are secure before switching on.",
                "Do not exceed 12V supply voltage.",
            ],
            "simulation": {
                "tools": ["BEAKER", "DROPPER_ACID"],
                "prefill": {"WATER": 70, "ACID": 20},
                "reactions": ["electrolysis", "fizz"],
                "theme_color": "#00E5FF",
            },
        },
        {
            "id": "c10_e2",
            "name": "Reactivity Series of Metals",
            "aim": "To determine the relative reactivity of metals by observing reactions with acids.",
            "theory": (
                "The reactivity series is an arrangement of metals in decreasing order of their reactivity. "
                "More reactive metals displace less reactive metals from their salt solutions. "
                "The reaction rate with dilute acids (effervescence) indicates relative reactivity. "
                "Order (most to least reactive): K > Na > Ca > Mg > Al > Zn > Fe > Pb > Cu > Ag > Au."
            ),
            "apparatus": [
                "Test Tubes (×5) with rack",
                "Spatula",
                "Measuring Cylinder (10 mL)",
                "Dropper",
                "Marker and Labels",
            ],
            "chemicals": [
                "Magnesium ribbon (Mg)",
                "Zinc granules (Zn)",
                "Iron filings (Fe)",
                "Copper turnings (Cu)",
                "Dilute Hydrochloric Acid (HCl)",
            ],
            "steps": [
                "Label four test tubes: Mg, Zn, Fe, Cu.",
                "Add a small amount of each metal to its respective test tube.",
                "Pour 5 mL of dilute HCl into each test tube.",
                "Observe the rate of effervescence in each test tube.",
                "Record: Mg reacts vigorously, Zn moderately, Fe slowly, Cu not at all.",
                "Test each gas with a burning splint to confirm hydrogen production.",
                "Tabulate your results in order of decreasing reactivity.",
                "Draw a partial reactivity series based on your observations.",
            ],
            "safety": [
                "Dilute HCl is corrosive — avoid skin and eye contact.",
                "Magnesium reacts vigorously — add acid slowly.",
                "Perform the experiment in a fume cupboard if possible.",
                "Dispose of metal-acid waste in the designated container.",
            ],
            "simulation": {
                "tools": ["BEAKER", "DROPPER_ACID", "CONICAL"],
                "prefill": {"ACID": 60},
                "reactions": ["acid_base", "fizz"],
                "theme_color": "#FFD700",
            },
        },
    ],

    11: [
        {
            "id": "c11_e1",
            "name": "Flame Test for Metal Ions",
            "aim": "To identify metal ions present in unknown salts by observing the colour of their flame.",
            "theory": (
                "When metal salts are heated in a flame, electrons in the metal ions absorb energy and jump "
                "to higher energy levels. When they fall back, they emit light of specific wavelengths "
                "visible as characteristic flame colours. Each metal ion produces a unique colour: "
                "Li (crimson), Na (golden yellow), K (lilac), Ca (brick red), Cu (green), Sr (scarlet)."
            ),
            "apparatus": [
                "Bunsen Burner",
                "Nichrome Wire Loop (×6)",
                "Test Tubes (×6)",
                "Watch Glass",
                "Cobalt Blue Glass",
                "Clamp and Stand",
            ],
            "chemicals": [
                "Lithium Chloride (LiCl)",
                "Sodium Chloride (NaCl)",
                "Potassium Chloride (KCl)",
                "Calcium Chloride (CaCl₂)",
                "Copper(II) Chloride (CuCl₂)",
                "Concentrated Hydrochloric Acid (HCl) — for cleaning wire",
            ],
            "steps": [
                "Clean the nichrome wire by dipping it in HCl and holding in the Bunsen flame until colourless.",
                "Dip the clean wire into the first salt (LiCl) sample.",
                "Hold the wire in the hottest part of the Bunsen flame (just above inner blue cone).",
                "Observe and record the flame colour immediately.",
                "Repeat cleaning with HCl between each salt sample.",
                "For potassium: view through cobalt blue glass to filter the yellow sodium contamination.",
                "Test all six salts and record the characteristic colour for each.",
                "Use the results to identify two unknown salt samples provided.",
            ],
            "safety": [
                "Concentrated HCl produces toxic fumes — use in a well-ventilated area.",
                "Keep the Bunsen burner away from flammable materials.",
                "Do not touch the hot nichrome wire — use a clamp.",
                "Wear heat-resistant gloves and goggles.",
            ],
            "simulation": {
                "tools": ["BUNSEN", "DROPPER_WATER"],
                "prefill": {},
                "reactions": ["fire", "flame_test"],
                "theme_color": "#FF4500",
            },
        },
        {
            "id": "c11_e2",
            "name": "Determination of Melting Point",
            "aim": "To determine the melting point of naphthalene and assess its purity.",
            "theory": (
                "The melting point is the temperature at which a solid changes to a liquid at atmospheric pressure. "
                "A pure crystalline substance has a sharp, well-defined melting point. "
                "Impurities cause the melting point to decrease and the melting range to broaden. "
                "Naphthalene (C₁₀H₈) has a literature melting point of 80.2 °C."
            ),
            "apparatus": [
                "Capillary Tubes (sealed at one end)",
                "Melting Point Apparatus (or water bath)",
                "Thermometer (0–200 °C)",
                "Beaker (250 mL)",
                "Rubber Band",
                "Bunsen Burner",
                "Tripod and Wire Gauze",
                "Stirring Rod",
            ],
            "chemicals": [
                "Naphthalene (pure sample)",
                "Naphthalene (impure sample)",
                "Liquid Paraffin or Water (heating bath medium)",
            ],
            "steps": [
                "Powder a small amount of naphthalene on a watch glass using a spatula.",
                "Pack the naphthalene tightly into a sealed capillary tube (~1 cm depth).",
                "Attach the capillary tube to the thermometer with a rubber band at bulb level.",
                "Immerse in the heating bath (water bath at ~60°C to begin).",
                "Heat the bath slowly (~2°C per minute) while stirring continuously.",
                "Record the temperature at which the solid first begins to melt.",
                "Record the temperature at which the solid completely melts.",
                "Repeat with the impure sample; compare the melting ranges.",
            ],
            "safety": [
                "Naphthalene vapour is harmful — work in a well-ventilated area.",
                "Handle hot glassware with heat-resistant gloves.",
                "The thermometer is fragile — handle with care.",
                "Dispose of naphthalene in the organic waste container.",
            ],
            "simulation": {
                "tools": ["BEAKER", "BUNSEN"],
                "prefill": {"WATER": 60},
                "reactions": ["heating", "evaporation"],
                "theme_color": "#C084FC",
            },
        },
    ],

    12: [
        {
            "id": "c12_e1",
            "name": "Acid-Base Titration",
            "aim": "To determine the concentration of NaOH solution using standard HCl solution.",
            "theory": (
                "Titration is a quantitative analytical technique used to determine the concentration of "
                "an unknown solution by reacting it with a standard solution of known concentration. "
                "In acid-base titration, an acid and base react to form salt and water. "
                "The endpoint is detected using an indicator (phenolphthalein: pink → colourless). "
                "At equivalence: moles of acid = moles of base."
            ),
            "apparatus": [
                "Burette (50 mL) with stand",
                "Pipette (25 mL)",
                "Conical Flask (250 mL) × 3",
                "Beaker (100 mL)",
                "Funnel (small)",
                "White Tile",
                "Clamp and Stand",
                "Wash Bottle",
            ],
            "chemicals": [
                "Standard HCl solution (0.1 M)",
                "NaOH solution (unknown concentration)",
                "Phenolphthalein indicator",
                "Distilled Water",
            ],
            "steps": [
                "Rinse the burette with distilled water, then with the HCl solution.",
                "Fill the burette with standard HCl (0.1 M) up to the 0.00 mL mark.",
                "Use a pipette to transfer 25 mL of NaOH solution into the conical flask.",
                "Add 2–3 drops of phenolphthalein; the solution turns pink.",
                "Add HCl from the burette dropwise, swirling the flask continuously.",
                "As the pink colour begins to fade near the endpoint, add HCl drop by drop.",
                "Stop at the first permanent colourless endpoint (lasts 30 seconds).",
                "Record the final burette reading. Repeat to get 3 concordant titres.",
            ],
            "safety": [
                "HCl is corrosive — avoid skin/eye contact; wear goggles and gloves.",
                "NaOH is caustic — rinse with copious water if contact occurs.",
                "Do not pipette by mouth — always use a pipette filler.",
                "Dispose of acid-base waste by diluting with water before pouring.",
            ],
            "simulation": {
                "tools": ["BURETTE", "CONICAL", "BEAKER", "DROPPER_ACID", "DROPPER_BASE", "DROPPER_INDICATOR"],
                "prefill": {"BASE": 80},
                "reactions": ["acid_base", "neutralization", "color_change"],
                "reaction_rules": ["HCl + NaOH -> NaCl + H2O"],
                "success_conditions": ["endpoint_reached", "stable_colourless_solution"],
                "titration": True,
                "theme_color": "#F472B6",
            },
        },
        {
            "id": "c12_e2",
            "name": "Paper Chromatography",
            "aim": "To separate and identify the components of a mixture of dyes using paper chromatography.",
            "theory": (
                "Chromatography is a separation technique based on differential migration of components "
                "across a stationary phase carried by a mobile phase (solvent). "
                "In paper chromatography, the paper acts as the stationary phase and the solvent moves "
                "up by capillary action (mobile phase). Components with higher solubility in the solvent "
                "travel further. The Rf value = (distance travelled by spot) / (distance travelled by solvent)."
            ),
            "apparatus": [
                "Chromatography Paper Strips (×3)",
                "Beaker (250 mL, tall-form)",
                "Pencil and Ruler",
                "Capillary Tubes (×4)",
                "Clips / Crocodile Clips",
                "Petri Dish",
                "UV Lamp (if fluorescent dyes)",
            ],
            "chemicals": [
                "Ink samples (black, blue, red, green)",
                "Solvent: Water or 1-butanol:acetic acid:water (12:3:5)",
                "Unknown dye mixture (for identification)",
            ],
            "steps": [
                "Cut a strip of chromatography paper slightly shorter than the beaker height.",
                "Draw a faint pencil baseline 2 cm from the bottom of the strip.",
                "Use a capillary tube to spot each ink sample at marked positions on the baseline.",
                "Allow spots to dry; re-spot twice more to concentrate the sample.",
                "Pour ~1 cm depth of solvent into the beaker (below the baseline level).",
                "Suspend the paper strip in the beaker — baseline must be above solvent level.",
                "Cover the beaker and allow the solvent to rise (do not disturb).",
                "Remove the strip when the solvent front is near the top; mark the front immediately.",
                "Allow to dry; measure the distance of each spot and the solvent front.",
                "Calculate Rf values and compare with reference Rf values to identify components.",
            ],
            "safety": [
                "Organic solvents are flammable — keep away from flames.",
                "Work in a ventilated area when using organic solvents.",
                "Do not eat, drink or touch face during the experiment.",
                "Dispose of solvent waste in the organic waste container.",
            ],
            "simulation": {
                "tools": ["BEAKER", "DROPPER_WATER"],
                "prefill": {"WATER": 60, "ACID": 20},
                "reactions": ["mixing", "color_change"],
                "theme_color": "#34D399",
            },
        },
        {
            "id": "c12_e3",
            "name": "Esterification Reaction",
            "aim": "To prepare an ester from ethanol and acetic acid and observe its characteristic fruity smell.",
            "theory": (
                "Esterification is a chemical reaction in which an alcohol reacts with a carboxylic acid "
                "in the presence of concentrated sulphuric acid to form an ester and water. "
                "In this experiment, ethanol reacts with acetic acid to produce ethyl ethanoate, "
                "a sweet-smelling ester. The reaction is slow at room temperature, so gentle heating "
                "in a water bath helps the reaction proceed."
            ),
            "apparatus": [
                "Test Tube",
                "Beaker",
                "Hot Water Bath",
                "Dropper",
                "Bunsen Burner",
                "Tripod Stand",
                "Wire Gauze",
                "Glass Rod",
            ],
            "chemicals": [
                "Ethanol (C₂H₅OH)",
                "Glacial Acetic Acid (CH₃COOH)",
                "Concentrated Sulphuric Acid (H₂SO₄)",
                "Distilled Water",
                "Sodium Carbonate Solution (Na₂CO₃)",
            ],
            "steps": [
                "Take about 2 mL of ethanol in a clean test tube.",
                "Add about 2 mL of glacial acetic acid to the same test tube.",
                "Add a few drops of concentrated sulphuric acid carefully as a catalyst.",
                "Place the test tube in a warm water bath for 5 minutes.",
                "Pour the reaction mixture into a beaker containing sodium carbonate solution.",
                "Observe effervescence as excess acid is neutralized.",
                "Gently smell the vapour by wafting it towards your nose.",
                "Record the fruity smell that indicates formation of an ester.",
            ],
            "safety": [
                "Concentrated sulphuric acid is highly corrosive — add it slowly and carefully.",
                "Ethanol is flammable — keep it away from direct flame.",
                "Use a water bath instead of heating the test tube directly.",
                "Do not smell chemicals directly; always waft vapours gently.",
            ],
            "simulation": {
                "tools": ["TEST_TUBE", "BEAKER", "WATER_BATH", "DROPPER_ACID", "DROPPER_WATER", "BUNSEN"],
                "prefill": {"ALCOHOL": 30, "ACID": 30, "WATER": 40},
                "reactions": ["esterification", "neutralization", "mixing"],
                "theme_color": "#A3E635",
            },
        },
    ],
}

for _class_num, _json_experiments in load_json_experiments().items():
    existing = EXPERIMENTS.setdefault(_class_num, [])
    existing_ids = {exp["id"] for exp in existing}
    for _exp in _json_experiments:
        if _exp["id"] not in existing_ids:
            existing.append(_exp)


def _chemical_category(label: str):
    """Map experiment chemical labels to the generic simulator buckets."""
    text = label.lower()

    if "water" in text:
        return "water"
    if ("indicator" in text or "phenolphthalein" in text):
        return "indicator"
    if ("alcohol" in text or "ethanol" in text):
        return "alcohol"
    if (
        "acid" in text or "hcl" in text or "h₂so₄" in text or "h2so4" in text
        or "ch₃cooh" in text or "ch3cooh" in text or "vinegar" in text
        or "lemon juice" in text
    ):
        return "acid"
    if (
        "base" in text or "naoh" in text or "nahco₃" in text or "nahco3" in text
        or "naocl" in text or "soap" in text or "bleach" in text
        or "alkaline" in text or "carbonate" in text or "na₂co₃" in text
        or "na2co3" in text
    ):
        return "base"
    if (
        "salt" in text or "nacl" in text or "chloride" in text
        or "sulphate" in text or "sulfate" in text
    ):
        return "salt"
    return None


def _chemical_color(label: str, category: str):
    """Approximate real-life display colour for a selected experiment chemical."""
    text = label.lower()

    if "distilled water" in text or text.strip() == "water":
        return (255, 214, 160)
    if "phenolphthalein" in text:
        return (240, 230, 230)
    if "universal indicator" in text:
        return (70, 170, 255)
    if "hcl" in text or "hydrochloric" in text:
        return (235, 235, 175)
    if "h₂so₄" in text or "h2so4" in text or "sulphuric acid" in text:
        return (230, 245, 190)
    if "vinegar" in text:
        return (200, 230, 255)
    if "lemon juice" in text:
        return (120, 220, 255)
    if "naoh" in text or "sodium hydroxide" in text:
        return (255, 230, 220)
    if "soap" in text:
        return (255, 210, 170)
    if "baking soda" in text or "nahco₃" in text or "nahco3" in text:
        return (255, 220, 205)
    if "bleach" in text or "naocl" in text:
        return (170, 235, 235)
    if "nacl" in text or "salt solution" in text or "common salt" in text:
        return (245, 235, 205)
    if "milk" in text:
        return (235, 245, 255)
    if "alcohol" in text or "ethanol" in text:
        return (235, 245, 215)

    defaults = {
        "water": (255, 214, 160),
        "acid": (235, 235, 175),
        "base": (255, 230, 220),
        "salt": (245, 235, 205),
        "indicator": (120, 205, 255),
        "alcohol": (235, 245, 215),
    }
    return defaults.get(category, (220, 220, 220))


def get_chemical_profile(selection: str):
    """
    Return normalized metadata for a selected chemical label.
    Keeps the generic category for reactions while preserving
    a more realistic label and display colour for the UI.
    """
    category = _chemical_category(selection) or "water"
    return {
        "category": category,
        "display_name": selection,
        "color_bgr": _chemical_color(selection, category),
    }


def get_chemical_options(exp_data):
    """
    Return experiment-specific simulator chemical options grouped by
    the generic liquid keys used by the renderer/reaction system.
    """
    grouped = {k: [] for k in ["water", "acid", "base", "salt", "indicator", "alcohol"]}

    for item in exp_data.get("chemicals", []):
        category = _chemical_category(item)
        if not category:
            continue
        grouped[category].append(item)

    if any(grouped.values()):
        return {key: values for key, values in grouped.items() if values}

    return {"water": ["Distilled Water"]}


def get_simulation_apparatus(exp_data):
    """Return simulator apparatus keys relevant to a given experiment."""
    mapping = {
        "BEAKER": "beaker",
        "TEST_TUBE": "test_tube",
        "CYLINDER": "cylinder",
        "BUNSEN": "bunsen",
        "WATER_BATH": "water_bath",
        "CONICAL": "flask",
        "FLASK": "flask",
        "DROPPER_WATER": "dropper",
        "DROPPER_ACID": "dropper",
        "DROPPER_BASE": "dropper",
        "DROPPER_INDICATOR": "dropper",
        "BURETTE": "burette",
    }

    tools = exp_data.get("simulation", {}).get("tools", [])
    result = []

    for tool in tools:
        apparatus = mapping.get(tool)
        if apparatus and apparatus not in result:
            result.append(apparatus)

    apparatus_text = " ".join(exp_data.get("apparatus", [])).lower()
    if "burette" in apparatus_text and "burette" not in result:
        result.append("burette")
    if "pipette" in apparatus_text and "dropper" not in result:
        result.append("dropper")

    if not result:
        result = ["beaker", "test_tube", "flask", "dropper", "cylinder", "bunsen"]

    return result


def get_classes():
    """Return list of available class numbers."""
    return sorted(EXPERIMENTS.keys())


def get_experiments(class_num):
    """Return list of experiments for a given class."""
    return EXPERIMENTS.get(class_num, [])


def get_experiment(exp_id):
    """Find and return a specific experiment by its ID."""
    for cls_experiments in EXPERIMENTS.values():
        for exp in cls_experiments:
            if exp["id"] == exp_id:
                return exp
    return None
