#!/usr/bin/env python3
"""
Script de test des animations et effets visuels
Teste toutes les animations CSS et JavaScript
"""

import webbrowser
import time
import os
import sys
from pathlib import Path

def print_banner():
    """Affiche la bannière de test"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    TEST ANIMATIONS QHSE IA                  ║
    ║                   Effets Visuels Avancés                    ║
    ║                                                              ║
    ║  🎨 Animations CSS:                                          ║
    ║     • Fade In/Out, Scale, Rotate                            ║
    ║     • Glow, Pulse, Shimmer                                   ║
    ║     • Typewriter, Neon Effects                              ║
    ║     • Gradient Animations                                    ║
    ║                                                              ║
    ║  ⚡ Effets JavaScript:                                       ║
    ║     • Particules flottantes                                 ║
    ║     • Ripple effects                                         ║
    ║     • Compteurs animés                                       ║
    ║     • Notifications toast                                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def test_css_animations():
    """Teste les animations CSS"""
    print("🎨 Test des animations CSS...")
    
    # Vérifier que le fichier CSS existe
    css_file = Path("interface/static/css/advanced-animations.css")
    if not css_file.exists():
        print("❌ Fichier CSS d'animations non trouvé!")
        return False
    
    print("✅ Fichier CSS d'animations trouvé")
    
    # Lire et analyser le contenu
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier les animations clés
    animations = [
        'fadeInUp', 'fadeInLeft', 'fadeInRight', 'scaleIn', 'rotateIn',
        'glow', 'pulse', 'shimmer', 'neonGlow', 'typewriter',
        'gradientShift', 'rainbow', 'cardHover', 'bounceIn'
    ]
    
    found_animations = []
    for animation in animations:
        if animation in content:
            found_animations.append(animation)
    
    print(f"✅ {len(found_animations)}/{len(animations)} animations CSS détectées")
    for anim in found_animations:
        print(f"   • {anim}")
    
    return len(found_animations) >= len(animations) * 0.8

def test_js_effects():
    """Teste les effets JavaScript"""
    print("\n⚡ Test des effets JavaScript...")
    
    # Vérifier que le fichier JS existe
    js_file = Path("interface/static/js/advanced-effects.js")
    if not js_file.exists():
        print("❌ Fichier JS d'effets non trouvé!")
        return False
    
    print("✅ Fichier JS d'effets trouvé")
    
    # Lire et analyser le contenu
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier les classes et méthodes clés
    js_features = [
        'AdvancedEffects', 'setupParticleSystem', 'createParticle',
        'setupTypingEffects', 'setupScrollAnimations', 'setupHoverEffects',
        'createRipple', 'animateCounter', 'showNotification'
    ]
    
    found_features = []
    for feature in js_features:
        if feature in content:
            found_features.append(feature)
    
    print(f"✅ {len(found_features)}/{len(js_features)} fonctionnalités JS détectées")
    for feature in found_features:
        print(f"   • {feature}")
    
    return len(found_features) >= len(js_features) * 0.8

def test_html_templates():
    """Teste les templates HTML animés"""
    print("\n📄 Test des templates HTML animés...")
    
    templates = [
        "interface/templates/dashboard_animated.html",
        "interface/templates/login_animated.html", 
        "interface/templates/form_animated.html"
    ]
    
    found_templates = []
    for template in templates:
        if Path(template).exists():
            found_templates.append(template)
            print(f"✅ {template}")
        else:
            print(f"❌ {template}")
    
    return len(found_templates) == len(templates)

def test_animation_classes():
    """Teste les classes d'animation CSS"""
    print("\n🔍 Test des classes d'animation...")
    
    css_file = Path("interface/static/css/advanced-animations.css")
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Classes d'animation importantes
    animation_classes = [
        '.animate-fadeInUp', '.animate-fadeInLeft', '.animate-fadeInRight',
        '.animate-scaleIn', '.animate-rotateIn', '.animate-glow',
        '.animate-pulse', '.animate-shimmer', '.animate-neonGlow',
        '.animate-typewriter', '.animate-gradient', '.animate-rainbow',
        '.animate-cardHover', '.animate-bounceIn', '.animate-float',
        '.animate-drift', '.animate-sparkle'
    ]
    
    found_classes = []
    for class_name in animation_classes:
        if class_name in content:
            found_classes.append(class_name)
    
    print(f"✅ {len(found_classes)}/{len(animation_classes)} classes d'animation détectées")
    
    return len(found_classes) >= len(animation_classes) * 0.8

def test_keyframes():
    """Teste les keyframes CSS"""
    print("\n🎬 Test des keyframes CSS...")
    
    css_file = Path("interface/static/css/advanced-animations.css")
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Keyframes importants
    keyframes = [
        '@keyframes fadeInUp', '@keyframes glow', '@keyframes pulse',
        '@keyframes shimmer', '@keyframes neonGlow', '@keyframes typewriter',
        '@keyframes gradientShift', '@keyframes rainbow', '@keyframes cardHover',
        '@keyframes bounceIn', '@keyframes float', '@keyframes drift',
        '@keyframes sparkle', '@keyframes spin', '@keyframes ripple'
    ]
    
    found_keyframes = []
    for keyframe in keyframes:
        if keyframe in content:
            found_keyframes.append(keyframe)
    
    print(f"✅ {len(found_keyframes)}/{len(keyframes)} keyframes détectés")
    
    return len(found_keyframes) >= len(keyframes) * 0.8

def test_responsive_animations():
    """Teste les animations responsives"""
    print("\n📱 Test des animations responsives...")
    
    css_file = Path("interface/static/css/advanced-animations.css")
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier les media queries
    responsive_features = [
        '@media (prefers-reduced-motion: reduce)',
        '@media (max-width: 768px)',
        'animation-duration: 0.01ms',
        'animation-iteration-count: 1'
    ]
    
    found_responsive = []
    for feature in responsive_features:
        if feature in content:
            found_responsive.append(feature)
    
    print(f"✅ {len(found_responsive)}/{len(responsive_features)} fonctionnalités responsives détectées")
    
    return len(found_responsive) >= len(responsive_features) * 0.5

def test_js_functionality():
    """Teste la fonctionnalité JavaScript"""
    print("\n🔧 Test de la fonctionnalité JavaScript...")
    
    js_file = Path("interface/static/js/advanced-effects.js")
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fonctionnalités JavaScript importantes
    js_functionality = [
        'class AdvancedEffects', 'constructor()', 'init()',
        'setupParticleSystem()', 'createParticle()', 'animateParticles()',
        'setupTypingEffects()', 'initTypewriter()', 'setupScrollAnimations()',
        'setupHoverEffects()', 'onHoverEnter()', 'onHoverLeave()',
        'createRipple()', 'setupLoadingAnimations()', 'animateCounter()',
        'showNotification()', 'createGlowEffect()'
    ]
    
    found_functionality = []
    for func in js_functionality:
        if func in content:
            found_functionality.append(func)
    
    print(f"✅ {len(found_functionality)}/{len(js_functionality)} fonctionnalités JS détectées")
    
    return len(found_functionality) >= len(js_functionality) * 0.8

def generate_test_report():
    """Génère un rapport de test"""
    print("\n📊 Génération du rapport de test...")
    
    tests = [
        ("Animations CSS", test_css_animations),
        ("Effets JavaScript", test_js_effects),
        ("Templates HTML", test_html_templates),
        ("Classes d'animation", test_animation_classes),
        ("Keyframes CSS", test_keyframes),
        ("Animations responsives", test_responsive_animations),
        ("Fonctionnalité JS", test_js_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    # Afficher le rapport
    print("\n" + "="*60)
    print("📋 RAPPORT DE TEST DES ANIMATIONS")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("="*60)
    print(f"Résultat: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! Les animations sont prêtes.")
    elif passed >= total * 0.8:
        print("⚠️  La plupart des tests sont passés. Quelques ajustements nécessaires.")
    else:
        print("❌ Plusieurs tests ont échoué. Vérifiez les fichiers.")
    
    return passed == total

def open_test_pages():
    """Ouvre les pages de test dans le navigateur"""
    print("\n🌐 Ouverture des pages de test...")
    
    base_url = "http://localhost:5000"
    test_pages = [
        ("Dashboard Animé", f"{base_url}/dashboard_animated"),
        ("Connexion Animée", f"{base_url}/login_animated"),
        ("Formulaire Animé", f"{base_url}/form_animated")
    ]
    
    for page_name, url in test_pages:
        print(f"Ouverture: {page_name}")
        try:
            webbrowser.open(url)
            time.sleep(1)  # Délai entre les ouvertures
        except Exception as e:
            print(f"❌ Erreur ouverture {page_name}: {e}")

def main():
    """Fonction principale"""
    print_banner()
    
    # Exécuter les tests
    success = generate_test_report()
    
    if success:
        print("\n🚀 Tests réussis! Ouverture des pages de test...")
        open_test_pages()
        
        print("\n💡 Instructions:")
        print("1. Vérifiez que l'application Flask est démarrée")
        print("2. Testez les animations dans le navigateur")
        print("3. Vérifiez la responsivité sur mobile")
        print("4. Testez les effets de survol et de clic")
        
    else:
        print("\n❌ Certains tests ont échoué. Vérifiez les fichiers.")
        print("💡 Assurez-vous que tous les fichiers sont créés correctement.")
    
    print("\n✨ Test des animations terminé!")

if __name__ == "__main__":
    main()
