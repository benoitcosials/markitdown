<!-- Slide number: 1 -->
# Gouvernance QADirection FSA
Benoit Cosials

<!-- Slide number: 2 -->
# Le QA c’est quoi.
Le QA fait partie intégrante du processus de livraison
Le QA permet de rendre les équipes et utilisateurs confiant dans la solution par la production de preuves d’exécutions de tests
Le QA permet de garantir que
La solution correspond au besoin des utilisateurs
La solution est robuste
La solution répond à une norme de l’industrie
Le processus de livraison est auditable
QA = Quality Assurance = Assurance qualité

### Notes:
Il ne remplace pas le processus de développement c’est une assurance de plus sur le résultat.

<!-- Slide number: 3 -->
# Le QA s’appuie sur ces éléments
Un scope précis et stable
Les besoins d’affaires et les solutions sont bien alignés
Le processus de livraison inclus des tests
L’environnement de test et les données sont bien maitrisés

### Notes:
Dire : Pour permettre de faire les tests il nous faut en premier lieu

<!-- Slide number: 4 -->
# Les QA travaillent avec vous 
Nous proposons des outils et des méthodes pour vous permettre :
De mesurer l’atteinte de vos objectifs de livraison avec des tests
Des guides pour améliorer les différentes étapes de la livraison en incluant des activités QA

### Notes:
Dire : Nous ne faisons pas d’architecture ou de développement, pas de gestion de projet, pas de processus d’affaires non plus…

<!-- Slide number: 5 -->
Décider d’un mode de livraison

<!-- Slide number: 6 -->
# Mode de livraison No 1
Traditionnel donc tout le monde comprend la méthode
Les Affaires peuvent découvrir des bug ou des fonctionnalités que les Dev doivent ajuster=> redo de tous les tests, dispo des Dev, retard de livraison
Implication des ressources dans des périodes différentes=> Impossible de garder une équipe dédiée
Q3
Q1
Q2
Q3
Feature 1
Feature 2
Feature 3
ACCP
Ajuster
INTG

![Utilisateur avec un remplissage uni](test_pptx/output_methodologie_images\slide6_image0.png)
DEV

![Utilisateur avec un remplissage uni](test_pptx/output_methodologie_images\slide6_image1.png)

![Utilisateur avec un remplissage uni](test_pptx/output_methodologie_images\slide6_image2.png)

![Utilisateur avec un remplissage uni](test_pptx/output_methodologie_images\slide6_image3.png)

![Utilisateur avec un remplissage uni](test_pptx/output_methodologie_images\slide6_image4.png)

![Utilisateur avec un remplissage uni](test_pptx/output_methodologie_images\slide6_image5.png)
Développeur
Analyste
Affaires

### Notes:

<!-- Slide number: 7 -->
# Mode No 1  - Avant de se lancer
Préparer un environnement de livraison
Scope des systèmes touchés par bloque (voir vericity)
Valider la disponibilité des ressources
Spécialistes TI et affaires
Environnements
Calendriers
Rafraichissements systématiques
Périodes critiques du processus
Critères de succès
Détecter les équipes qui travaillent sur les mêmes systèmes en même temps
Gestion des limites de systèmes pour les tests et les mock
Qualité de la stratégie de test(démarrer les tests plus tôt, juste à temps juste assez)
Qualité et facilité de gestion des données

### Notes:
Passé du mode réactif au mode planifié
Pour chaque acteur, fournir des informations d’aide à la décision et des guides de prise de décsion

<!-- Slide number: 8 -->
# Mode de livraison No 2
Non traditionnel, corrige les principaux défauts mais demande une adaptation de tous
Toute l’équipe est engagée au même moment=> équipe dédié possible=> correction ou ajustement de solution plus rapide
On a besoin que d’1 environnement
On peut aller en PROD avec une solution qui ne couvre pas tous les besoins
Pour être rapide, il faut automatiser les tâches, spécialement les essais
Q3
Q1
Q2
Feature 3
Feature 1
Feature 2
ENV
ACCP
INTG

DEV CONFIG

![Utilisateur avec un remplissage uni](test_pptx/output_methodologie_images\slide8_image0.png)

![Utilisateur avec un remplissage uni](test_pptx/output_methodologie_images\slide8_image1.png)

![Utilisateur avec un remplissage uni](test_pptx/output_methodologie_images\slide8_image2.png)

### Notes:

<!-- Slide number: 9 -->
# Mode No 2  - Avant de se lancer
Préparer un environnement de livraison
Préparer l’infrastructure et les coquilles de composant
Préparer la sécurité
Établir un model documentaire pour les spécifications
Préparer les outils de test automatisé
Avoir le groupe de testeurs prêts
Écrire la stratégie de test
Stratégie de gestion de données
Critères de succès
Environnement prêt => Pas de préparation à faire pendant la livraison
Utilisateurs testeur prêt=> ils ont connaissance du mode de livraison et de leurs participations
Équipe de livraison prête=> Ils ont connaissance du mode de livraion et de leur pariticpation

<!-- Slide number: 10 -->
# Mode 2 - Comment l’exécuter
Architectes et PO
Analyste et Concepteur
Développeurs et configurateur des système
Proposer une architecture par Feature
Identifier le processus
Identifier les éléments technologiques
Identifier les parties prenantes et leurs attentes
Fonctionnelles
non-fonctionnelles

Concrétiser la solution en respectant les limites de la Feature
Déterminer un model opérationnel « cible » (MOC)
Déterminer une chaine de traitement et ses composants TI
Créer des jeux de données « cible » pour chaque étape du MOC
Créer des maquettes des interfaces utilisateurs
Écrire les tests automatisés pour les composants, les intégrations et l’acceptation
Réaliser les spécifications des analystes et concepteur en utilisant les tests pour ce mesurer
Identifier tous les composants à modifier
Développer les composants et configurer les systèmes
Exécuter les tests automatisés pour vérifier que tout répond
Faire la MEP

<!-- Slide number: 11 -->
# Processus de livraison TI + QA
Écrire les tests
Prêt à planifier?
Prêt à réaliser?
Prêt à tester?
Prêt pour la PROD?
En vert les activité QA
Environnements de développements
Environnements d’essais
Environnements de prod

### Notes:
Le processus d’architecture livre :
Liste des items lié au processus d’affaire
Liste des items liés au Enabler
Liste des items lié au NFR

Qu’arrive t’il si on  ne passe pas la barrière « Prêt »
On reste là, On continue, on annule, etc

Deliver : Transfert de connaissance + Document de support