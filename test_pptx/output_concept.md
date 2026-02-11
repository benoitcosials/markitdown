<!-- Slide number: 1 -->

![Une image contenant plein air, ciel, Véhicule terrestre, personne Le contenu généré par l’IA peut être incorrect.](test_pptx/output_concept_images\slide1_image0.jpeg)
# Standard QAAffaires, SYSTÈME et TI
Concepts de base
13 novembre 2025

<!-- Slide number: 2 -->
# Agenda
01 	Objectifs des ateliers
02 	Release management
03 	Responsabilité et workflow
04	Niveaux de test
05 	Les plans de test
2

<!-- Slide number: 3 -->

Ces ateliers visent à :
Harmoniser les pratiques QA,
Clarifier les rôles et responsabilités,
Structurer les processus de test et
Assurer une meilleure coordination entre les différentes parties prenantes afin de garantir la qualité des livraisons.
# Objectifs des ateliers QA

<!-- Slide number: 4 -->
Le contexte du Release Management
@Jonathan Roberge
4

<!-- Slide number: 5 -->

Release management

| Qu’est-ce qu’un release manager |
| --- |
Le Release Manager est comme un chef d’orchestre qui s’assure que toutes les parties d’une livraison s’assemblent correctement et sont livrées aux utilisateurs sans problème.
Grâce à son rôle de coordination, il rationalise et optimise l’utilisation des paliers afin d’éviter toute contention entre les projets.
Il veille à la bonne application des processus d’essais et de livraison, tout en accompagnant les projets pour en garantir la conformité.
Prendre note, qu’il ne remplace pas les chargés de projet qui font le suivi en premier niveau avec leur équipe.

### Notes:
Le Release manager coordonnent et collabore avec les CP pour assurer l’ensemble des livraisons

<!-- Slide number: 6 -->
| MANDAT commun de Philippe, Andréa, Isabelle, Josée |
| --- |
Release management
| OBJECTIFS |
| --- |
Diminuer les erreurs lors de la mise en production
Optimiser les délais de livraison
Respecter les budgets
Minimiser les conflits entre différents projets
Régler les enjeux liés aux livraisons et faciliter le travail: audit et standardisation pour les nouveaux

<!-- Slide number: 7 -->
Responsabilité et
Workflow
@Benoit Cosials
7

<!-- Slide number: 8 -->
# Workflow entre les équipes de livraison et les  équipes contributrices
Le chargé de projet est responsable de la livraison et doit :
Gérer le Change Request dans ServiceNow
Superviser et valider le plan de test dans DevOps
Pour assurer une coordination efficace, l’équipe de livraison :
Coordonne les activités des équipes contributrices et les plans de mise en production (MEP)
Fournit un plan de test commun où les équipes contributrices devront inscrire leurs tests

8

### Notes:
Si votre équipe est responsable de la livraison de la Feature, vous serez responsable de piloter les essais
Vous devez organiser l'écriture, l'exécution des tests avec leur preuve d'exécution.

Si c'est une autre équipe qui est responsable de la livraison de la Feature, vous serez responsable de contribuer à leur plan de test.
Vous recevrez une suite de test représentant les travaux de votre Feature dans leur plan de test.
Ils devront vous indiquer avec qui et quand écrire, exécuter et collecter les preuves de test

<!-- Slide number: 9 -->
# Responsabilité dans l’équipe
| Responsable | Activités | Livrables |
| --- | --- | --- |
| DEV | Contrôler la qualité du code livré Contribuer à la Release Note Exécuter les tests de composant | Résultats des tests unitaires Documentation technique à jour |
| ANALYSTE​ | Produit les spécifications fonctionnelles et non-fonctionnelles des développements Contribuer à la Release Note Mettre à jour la documentation pour les utilisateurs et le support | - Documentation des spécifications |
| QA | Appliquent le standard QA du secteur Exécuter les tests Systèmes et intégration de systèmes Gérer les tests Gérer les bogues (Créer, Tester et Fermer) Rapport sur la qualité | Stratégie de test Test Plan Backlog ou le tableau de bord des bugs |
9

### Notes:
Ces éléments doivent être connue et documenté dans le release note qui devient un document central de la livraison

CP/SM Arrimage avec Release managment

Architecte : Preuve de conformité Archi - livraison

<!-- Slide number: 10 -->
# Responsabilité dans l’équipe
| Responsable | Activités | Livrables |
| --- | --- | --- |
| CP/SM | Assurer le suivi des Change Request, et des Plans de Test Organiser la rencontre de Go/No-Go | - Change Request dans Service Now |
| ARCHITECTE | Confirmer que la solution livrée est conforme à l’architecture approuvée, avant le début des tests systèmes | Documentation d’architecture Revue de la conception vs l’architecture |
| CONCEPTEUR | Produire la conception des solutions Réviser la qualité du code Déployer et vérifier que le code testé en ACCP correspond à celui déployé en PROD | - Numéro et date du commit |
| PO​ | - Documenter la release note avec les développeurs et analystes | - Release note à communiquer |
10

### Notes:
Ces éléments doivent être connue et documenté dans le release note qui devient un document central de la livraison

CP/SM Arrimage avec Release managment

Architecte : Preuve de conformité Archi - livraison

<!-- Slide number: 11 -->
Niveaux de test
@Sahar El Aida
11

<!-- Slide number: 12 -->
# Les niveaux de test : une pyramide de confiance

Les niveaux système et composants incluent aussi des tests d’intégration pour s’assurer que les modules et systèmes interagissent correctement.

<!-- Slide number: 13 -->
# Tests de composants & Tests d'intégration de composants
|  | Tests de composants/unitaires | Tests d'intégration de composants |
| --- | --- | --- |
| Objectifs des tests | Vérifier les composants individuels (unités de code), dans le but de cibler les défauts de la logique interne | Vérifier les Interfaces entre composants dans le but de détecter les défauts d’interaction entre composants |
| Responsabilités | Développeurs | Développeurs / QA |
| Environnements | Environnement de développement | Environnement de développement |
13

### Notes:

<!-- Slide number: 14 -->
# Tests Système & Tests d'intégration de système
|  | Tests système | Tests d'intégration système |
| --- | --- | --- |
| Objectifs des tests | Vérifier le système complet(E2E,performance...), en se basant sur les spécifications système et les exigences fonctionnelles, dans le but de détecter les défauts fonctionnels et non-fonctionnels. | Vérifier les interfaces entre systèmes et services externes, en se basant les Specs d'intégration et les contrats d'interface dans le but de détecter les défauts d'interopérabilité |
| Responsabilités | QA | QA / Intégrateurs |
| Environnements | Environnement de test | Environnement de test |
14

<!-- Slide number: 15 -->
# Tests d'Acceptation

|  | Tests d'acceptation |
| --- | --- |
| Objectifs des tests | Validation du système complet par les utilisateurs. Vérifier que la solution répond aux exigences métiers, contrats et réglementations. Le but est de détecter des défauts liés aux besoins métier. |
| Responsabilités | Utilisateurs, clients, parties prenantes |
| Environnements | Environnement pré-production |
15

<!-- Slide number: 16 -->
# Tester tôt, c’est gagner du temps et de la qualité

![](test_pptx/output_concept_images\slide16_image0.png)
Plus on test tôt, plus on réduit les coûts.

On détecte les défauts avant qu'ils ne deviennent critiques.

On améliore la confiance dans le produit.

16

<!-- Slide number: 17 -->
les plans de test
@Meriem Jedidi
17

<!-- Slide number: 18 -->
# Objectifs
18

### Notes:

<!-- Slide number: 19 -->
# Organisation du plan de test (DevOps)
N2
N3 & N4
Autant de User Story que de système à modifier/équipe contributrice
Suite décision Release Management
19

### Notes:
Smoke Test : vérifie si les fonctionnalités essentielles d'une application fonctionnent correctement après la fusion et la publication d'une nouvelle version.

<!-- Slide number: 20 -->
# Exemple : Trésorerie

![](test_pptx/output_concept_images\slide20_image0.png)
20

### Notes:

<!-- Slide number: 21 -->
Nos attentes
@Meriem Jedidi
21

<!-- Slide number: 22 -->
# Les attentes de nos directions affaires, systèmes et TI
22

### Notes: