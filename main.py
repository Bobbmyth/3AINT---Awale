"""
Main - Point d'entrée principal pour le jeu d'Awalé avec Pygame.
Ce script lance l'application complète du jeu d'Awalé avec l'interface Pygame.

Utilisation:
    python main.py

Fichiers requis:
    • awale.py
    • sommet.py
    • mcts.py
    • interface_pygame.py
"""

import sys
import os
import pygame

# Ajouter le répertoire courant au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verifier_fichiers():
    """Vérifie que tous les fichiers nécessaires sont présents."""
    fichiers_requis = [
        "awale.py",
        "sommet.py",
        "mcts.py",
        "interface_pygame.py"
    ]
    
    fichiers_manquants = []
    for fichier in fichiers_requis:
        if not os.path.exists(fichier):
            fichiers_manquants.append(fichier)
    
    return fichiers_manquants


def verifier_dependances():
    """Vérifie que les dépendances sont installées."""
    try:
        import pygame
        print("✅ Pygame installé")
        return True
    except ImportError:
        print("❌ Pygame non installé")
        print("   Installation: pip install pygame")
        return False


def menu_principal():
    """Affiche le menu principal et retourne le choix."""
    print("\n" + "=" * 70)
    print("🎮 AWALÉ - Jeu de Stratégie Africain 🎮")
    print("=" * 70)
    print("\n Modes de jeu disponibles:\n")
    print("  1️⃣  Joueur vs Joueur")
    print("  2️⃣  Joueur vs IA (MCTS)")
    print("  3️⃣  IA (MinMax) vs IA (MCTS)")
    print("  0️⃣  Quitter")
    print("\n" + "-" * 70)
    
    while True:
        choix = input("\nVotre choix (0-3): ").strip()
        if choix in ['0', '1', '2', '3']:
            return choix
        print("❌ Choix invalide. Veuillez entrer 0, 1, 2 ou 3.")


def main():
    """Point d'entrée principal."""
    print("\n" + "=" * 70)
    print("🎮 Bienvenue dans AWALÉ - Jeu de Stratégie Africain 🎮")
    print("=" * 70)
    
    # Vérifier les fichiers
    print("\n📁 Vérification des fichiers...")
    fichiers_manquants = verifier_fichiers()
    
    if fichiers_manquants:
        print("❌ Fichiers manquants:")
        for fichier in fichiers_manquants:
            print(f"  • {fichier}")
        print("\nAssurez-vous que tous les fichiers sont dans le même dossier.")
        sys.exit(1)
    
    print("✅ Tous les fichiers sont présents")
    
    # Vérifier les dépendances
    print("\n📦 Vérification des dépendances...")
    if not verifier_dependances():
        sys.exit(1)
    
    # Initialiser Pygame
    print("\n🎨 Initialisation de Pygame...")
    try:
        pygame.init()
        print("✅ Pygame initialisé")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de Pygame: {e}")
        sys.exit(1)
    
    # Menu principal
    while True:
        choix = menu_principal()
        
        if choix == '0':
            print("\n👋 Au revoir et merci d'avoir joué!")
            pygame.quit()
            sys.exit(0)
        
        try:
            # Importer les modules nécessaires
            from awale import awale
            from interface_pygame import InterfaceAwalePygame
            
            # Créer une instance du jeu selon le choix
            if choix == '1':
                # Joueur vs Joueur
                print("\n🎮 Lancement: Joueur vs Joueur")
                jeu = awale("Joueur 1", "Joueur 2")
            
            elif choix == '2':
                # Joueur vs IA (MCTS)
                print("\n🎮 Lancement: Joueur vs IA (MCTS)")
                jeu = awale("Vous", "IA MCTS")
            
            elif choix == '3':
                # IA vs IA
                print("\n🎮 Lancement: IA (MinMax) vs IA (MCTS)")
                jeu = awale("IA MinMax", "IA MCTS")
            
            # Lancer l'interface graphique
            print("📱 Lancement de l'interface graphique...")
            print("\nContrôles:")
            print("  • Cliquez sur une case pour jouer")
            print("  • Appuyez sur ESC pour retourner au menu")
            print("\n" + "=" * 70 + "\n")
            
            # ⭐ IMPORTANT: Passer l'instance du jeu à l'interface!
            interface = InterfaceAwalePygame(jeu)
            interface.run()
            
            # De retour au menu après la partie
            print("\n✅ Partie terminée. Retour au menu...")
        
        except ImportError as e:
            print(f"\n❌ Erreur d'import: {e}")
            print("\nAssurez-vous que tous les fichiers sont présents:")
            print("  • awale.py")
            print("  • sommet.py")
            print("  • mcts.py")
            print("  • interface_pygame.py")
            sys.exit(1)
        
        except Exception as e:
            print(f"\n❌ Une erreur s'est produite: {e}")
            import traceback
            traceback.print_exc()
            print("\nRetour au menu...")
            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir et merci d'avoir joué!")
        import pygame
        pygame.quit()
        sys.exit(0)