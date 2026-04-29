import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from scipy import stats
import matplotlib.ticker as ticker

# Configuration de la page
st.set_page_config(
    page_title=" Analyse du marché Immobilier ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Personnalisation CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #006633 0%, #004d26 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .property-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #006633;
        margin: 0.5rem 0;
    }
    .price-badge {
        font-size: 1.5rem;
        font-weight: bold;
        color: #006633;
    }
    .metric-card {
        background: linear-gradient(135deg, #006633 0%, #004d26 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    .fcfa-symbol {
        font-weight: bold;
        color: #006633;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# En-tête
st.markdown("""
<div class="main-header">
    <h1> Résidence élite </h1>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR - Navigation simplifiée
# ============================================
with st.sidebar:
    st.title(" Navigation")
    page = st.radio(
        "Choisissez une section",
        [
            " Collecte de données",
            " Analyse descriptive",
            " Corrélations"
        ]
    )

    st.markdown("---")
    st.caption(" TP INF232 EC 2 - Analyse de données ")
    st.caption(" Secteur: Immobilier ")
    st.caption(" Unité: Francs CFA ( FCFA) ")
    
    # Afficher le nombre de biens
    try:
        df_count = pd.read_csv("biens_immobiliers.csv")
        st.caption(f" Biens enregistrés : {len(df_count)}")
    except:
        st.caption(" Biens enregistrés : 0 ")

# ============================================
# INITIALISATION DU FICHIER DE DONNÉES
# ============================================
DATA_FILE = "biens_immobiliers.csv"

def init_dataframe():
    """Crée un DataFrame vide avec les bonnes colonnes"""
    columns = {
        "Date": [],
        "Nom_Proprietaire": [],
        "Matricule_Proprietaire": [],
        "Type_Bien": [],
        "Ville": [],
        "Quartier": [],
        "Surface": [],
        "Nombre_Pieces": [],
        "Nombre_Chambres": [],
        "Nombre_SDB": [],
        "Annee_Construction": [],
        "Etat_Bien": [],
        "Parking": [],
        "Balcon_Terrasse": [],
        "Piscine": [],
        "Prix_Demande": [],
        "Prix_M2": []
    }
    df = pd.DataFrame(columns)
    df.to_csv(DATA_FILE, index=False)
    return df

# Chargement des données
try:
    df = pd.read_csv(DATA_FILE)
    if df.empty:
        df = init_dataframe()
    else:
        # Conversion des types numériques
        numeric_cols = ['Surface', 'Nombre_Pieces', 'Nombre_Chambres', 'Nombre_SDB', 
                       'Annee_Construction', 'Prix_Demande', 'Prix_M2']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
except FileNotFoundError:
    df = init_dataframe()

# ============================================
# FONCTIONS UTILITAIRES
# ============================================
def is_matricule_unique(matricule, df_existant):
    """Vérifie l'unicité du matricule"""
    if df_existant.empty:
        return True
    return matricule not in df_existant['Matricule_Proprietaire'].values

def format_fcfa(prix):
    """Formate un prix en FCFA avec séparateurs"""
    return f"{prix:,.0f} FCFA"

def format_axis_integer(ax):
    """Formate les axes pour afficher des entiers sans virgules"""
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{int(x):,}'))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'{int(y):,}'))
    return ax

# ============================================
# SECTION 1: COLLECTE DE DONNÉES
# ============================================
if page == " Collecte de données":
    st.header(" Formulaire d'enregistrement d'un bien immobilier")
    
    # Informations du propriétaire
    st.subheader(" Informations du propriétaire")
    col_id1, col_id2 = st.columns(2)
    with col_id1:
        nom_proprietaire = st.text_input("Nom complet du propriétaire", placeholder="Ex: De L'Or")
    with col_id2:
        matricule_proprietaire = st.text_input("Matricule_Proprietaire ou numéro de la CNI", placeholder="Ex: 24G2114")
    
    st.markdown("---")
    
    with st.form("immobilier_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(" Caractéristiques du bien")
            type_bien = st.selectbox("Type de bien", ["Appartement", "Maison", "Studio", "Duplex", "Loft", "Villa"])
            
            # Ville et Quartier - saisie libre
            ville = st.text_input("Ville", placeholder="Ex: Douala, Yaoundé, Bandjoun, Bayangam...")
            quartier = st.text_input("Quartier", placeholder="Ex: Bonapriso, Bastos, Madagascar, Tsinga...")
            
            surface = st.number_input("Surface habitable (m²)", min_value=10, max_value=5000, value=70)
            nombre_pieces = st.number_input("Nombre de pièces", min_value=1, max_value=20, value=3)
            nombre_chambres = st.number_input("Nombre de chambres", min_value=0, max_value=10, value=2)
            nombre_sdb = st.number_input("Nombre de salles de bain", min_value=0, max_value=15, value=1)
        
        with col2:
            st.subheader(" État et construction")
            annee_construction = st.number_input("Année de construction", min_value=2000, max_value=2026, value=2015)
            etat_bien = st.select_slider("État général", ["À rénover", "Bon état", "Très bon état", "Neuf/Rénové"])
            
            st.subheader(" Équipements")
            parking = st.radio("Parking", ["Non", "Oui"], horizontal=True)
            balcon = st.radio("Balcon/Terrasse", ["Non", "Oui"], horizontal=True)
            piscine = st.radio("Piscine", ["Non", "Oui"], horizontal=True)
            
            st.subheader(" Prix (en FCFA)")
            prix_demande = st.number_input("Prix de vente demandé (FCFA)", 
                                          min_value=20000, 
                                          max_value=500000000, 
                                          value=50000, 
                                          step=1000000,
                                          help="Exemple: 50.000.000 FCFA = 50 millions")
        
        # Calcul automatique du prix au m²
        if surface > 0:
            prix_m2 = prix_demande / surface
        else:
            prix_m2 = 0
        
        # Afficher un résumé
        if prix_demande > 0 and surface > 0:
            st.info(f" **Résumé**: {surface}m² ➜ {prix_m2:,.0f} FCFA/m²")
        
        submit = st.form_submit_button(" Enregistrer le bien", use_container_width=True)
        
        if submit:
            if not nom_proprietaire.strip():
                st.error(" Veuillez entrer le nom du propriétaire")
            elif not matricule_proprietaire.strip():
                st.error(" Veuillez entrer le matricule du propriétaire")
            elif not is_matricule_unique(matricule_proprietaire, df):
                st.error(f" Le matricule '{matricule_proprietaire}' existe déjà")
            elif not ville.strip():
                st.error(" Veuillez entrer le nom de la ville")
            elif surface <= 0:
                st.error(" La surface doit être supérieure à 0")
            elif prix_demande <= 0:
                st.error(" Le prix doit être supérieur à 0")
            else:
                nouvelle_donnee = pd.DataFrame([{
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Nom_Proprietaire": nom_proprietaire.strip().upper(),
                    "Matricule_Proprietaire": matricule_proprietaire.strip().upper(),
                    "Type_Bien": type_bien,
                    "Ville": ville.strip().title(),
                    "Quartier": quartier.strip().title() if quartier.strip() else "Non spécifié",
                    "Surface": surface,
                    "Nombre_Pieces": nombre_pieces,
                    "Nombre_Chambres": nombre_chambres,
                    "Nombre_SDB": nombre_sdb,
                    "Annee_Construction": annee_construction,
                    "Etat_Bien": etat_bien,
                    "Parking": parking,
                    "Balcon_Terrasse": balcon,
                    "Piscine": piscine,
                    "Prix_Demande": prix_demande,
                    "Prix_M2": prix_m2
                }])
                
                df_combine = pd.concat([df, nouvelle_donnee], ignore_index=True)
                df_combine.to_csv(DATA_FILE, index=False)
                
                st.markdown(f"""
                <div class="success-message">
                     <strong>Bien immobilier ajouté avec succès !</strong><br>
                     {type_bien} à {ville.strip().title()} - {surface}m² - {format_fcfa(prix_demande)} (soit {prix_m2:,.0f} FCFA/m²)
                </div>
                """, unsafe_allow_html=True)
                st.balloons()

# ============================================
# SECTION 2: ANALYSE DESCRIPTIVE
# ============================================
elif page == " Analyse descriptive":
    if df.empty:
        st.warning(" Aucune donnée disponible. Commencez par ajouter des biens immobiliers.")
    else:
        st.header(" Analyse descriptive du marché immobilier")
        
        # KPI principaux
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(" Nombre de biens", f"{len(df):,}")
        with col2:
            st.metric(" Prix moyen", format_fcfa(df['Prix_Demande'].mean()))
        with col3:
            st.metric(" Surface moyenne", f"{df['Surface'].mean():.0f} m²")
        with col4:
            st.metric(" Prix/m² moyen", f"{df['Prix_M2'].mean():,.0f} FCFA")
        with col5:
            if not df.empty:
                meilleur_bien = df.loc[df['Prix_M2'].idxmin()] if not df.empty else None
                if meilleur_bien is not None:
                    st.metric(" Meilleur rapport", f"{meilleur_bien['Ville']}\n{meilleur_bien['Prix_M2']:,.0f} FCFA/m²")
        
        st.markdown("---")
        
        # Onglets
        tab1, tab2, tab3, tab4 = st.tabs([
            " Distribution des prix", 
            " Prix par ville", 
            " Surface vs Prix",
            " Prix par type"
        ])
        
        with tab1:
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.histplot(df['Prix_Demande'], bins=20, kde=True, color='skyblue', ax=ax)
            ax.set_title("Distribution des prix immobiliers (FCFA)", fontsize=14, fontweight='bold')
            ax.set_xlabel("Prix (FCFA)", fontsize=12)
            ax.set_ylabel("Fréquence", fontsize=12)
            ax.axvline(df['Prix_Demande'].mean(), color='red', linestyle='--', linewidth=2,
                      label=f'Moyenne: {format_fcfa(df["Prix_Demande"].mean())}')
            ax.axvline(df['Prix_Demande'].median(), color='green', linestyle='--', linewidth=2,
                      label=f'Médiane: {format_fcfa(df["Prix_Demande"].median())}')
            ax.legend(fontsize=10)
            
            # Formatage des axes en entiers
            ax = format_axis_integer(ax)
            plt.tight_layout()
            st.pyplot(fig)
            
            # Statistiques détaillées
            st.subheader("Statistiques des prix (FCFA)")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"• **Minimum**: {format_fcfa(df['Prix_Demande'].min())}")
                st.write(f"• **25e percentile**: {format_fcfa(df['Prix_Demande'].quantile(0.25))}")
                st.write(f"• **Médiane**: {format_fcfa(df['Prix_Demande'].median())}")
            with col_b:
                st.write(f"• **75e percentile**: {format_fcfa(df['Prix_Demande'].quantile(0.75))}")
                st.write(f"• **Maximum**: {format_fcfa(df['Prix_Demande'].max())}")
                st.write(f"• **Écart-type**: {format_fcfa(df['Prix_Demande'].std())}")
        
        with tab2:
            # Top 10 des villes avec le plus de biens
            top_villes = df['Ville'].value_counts().head(10).index
            df_top = df[df['Ville'].isin(top_villes)]
            
            prix_par_ville = df_top.groupby('Ville')['Prix_Demande'].mean().sort_values(ascending=False)
            prix_m2_par_ville = df_top.groupby('Ville')['Prix_M2'].mean().sort_values(ascending=False)
            
            fig, axes = plt.subplots(1, 2, figsize=(14, 6))
            
            # Graphique des prix moyens par ville
            bars1 = axes[0].bar(range(len(prix_par_ville)), prix_par_ville.values, color='coral', edgecolor='black')
            axes[0].set_xticks(range(len(prix_par_ville)))
            axes[0].set_xticklabels(prix_par_ville.index, rotation=45, ha='right')
            axes[0].set_title("Prix moyen par ville (FCFA)", fontsize=12, fontweight='bold')
            axes[0].set_ylabel("Prix moyen (FCFA)", fontsize=11)
            
            # Ajout des valeurs sur les barres
            for bar, val in zip(bars1, prix_par_ville.values):
                axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + bar.get_height()*0.02,
                           f'{int(val):,}', ha='center', fontsize=9, rotation=0)
            
            # Graphique des prix au m² par ville
            bars2 = axes[1].bar(range(len(prix_m2_par_ville)), prix_m2_par_ville.values, color='teal', edgecolor='black')
            axes[1].set_xticks(range(len(prix_m2_par_ville)))
            axes[1].set_xticklabels(prix_m2_par_ville.index, rotation=45, ha='right')
            axes[1].set_title("Prix au m² moyen par ville (FCFA)", fontsize=12, fontweight='bold')
            axes[1].set_ylabel("Prix au m² (FCFA)", fontsize=11)
            
            # Ajout des valeurs sur les barres
            for bar, val in zip(bars2, prix_m2_par_ville.values):
                axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + bar.get_height()*0.02,
                           f'{int(val):,}', ha='center', fontsize=9, rotation=0)
            
            # Formatage des axes en entiers
            for ax in axes:
                ax = format_axis_integer(ax)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Tableau des villes
            st.subheader("Détail par ville")
            ville_stats = df.groupby('Ville').agg({
                'Prix_Demande': ['mean', 'min', 'max', 'count'],
                'Prix_M2': 'mean',
                'Surface': 'mean'
            }).round(0)
            ville_stats.columns = ['Prix moyen', 'Prix min', 'Prix max', 'Nb biens', 'Prix/m² moyen', 'Surface moy']
            ville_stats = ville_stats.sort_values('Prix moyen', ascending=False)
            
            # Formatage des colonnes de prix
            for col in ['Prix moyen', 'Prix min', 'Prix max']:
                ville_stats[col] = ville_stats[col].apply(lambda x: f"{int(x):,} FCFA")
            ville_stats['Prix/m² moyen'] = ville_stats['Prix/m² moyen'].apply(lambda x: f"{int(x):,} FCFA/m²")
            ville_stats['Surface moy'] = ville_stats['Surface moy'].apply(lambda x: f"{int(x):.0f} m²")
            
            st.dataframe(ville_stats, use_container_width=True)
        
        with tab3:
            fig, ax = plt.subplots(figsize=(12, 6))
            scatter = ax.scatter(df['Surface'], df['Prix_Demande'], 
                                c=df['Prix_M2'], cmap='viridis', 
                                s=80, alpha=0.6, edgecolors='black')
            ax.set_xlabel("Surface (m²)", fontsize=12)
            ax.set_ylabel("Prix (FCFA)", fontsize=12)
            ax.set_title("Relation Surface - Prix", fontsize=14, fontweight='bold')
            cbar = plt.colorbar(scatter, label="Prix au m² (FCFA)")
            
            # Régression linéaire
            slope, intercept, r_value, p_value, std_err = stats.linregress(df['Surface'], df['Prix_Demande'])
            x_line = np.array([df['Surface'].min(), df['Surface'].max()])
            y_line = intercept + slope * x_line
            ax.plot(x_line, y_line, 'r--', linewidth=2, label=f'Tendance (R²={r_value**2:.3f})')
            ax.legend(fontsize=10)
            
            # Formatage des axes en entiers
            ax = format_axis_integer(ax)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            correlation = df['Surface'].corr(df['Prix_Demande'])
            st.info(f" **Corrélation Surface-Prix**: {correlation:.3f}")
            st.caption("Plus la corrélation est proche de 1, plus la surface explique bien le prix")
        
        with tab4:
            prix_par_type = df.groupby('Type_Bien').agg({
                'Prix_Demande': 'mean',
                'Prix_M2': 'mean',
                'Surface': 'mean',
                'Matricule_Proprietaire': 'count'
            }).round(0).sort_values('Prix_Demande', ascending=False)
            prix_par_type = prix_par_type.rename(columns={'Matricule_Proprietaire': 'Nombre'})
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(range(len(prix_par_type)), prix_par_type['Prix_Demande'].values, 
                         color='skyblue', edgecolor='black')
            ax.set_xticks(range(len(prix_par_type)))
            ax.set_xticklabels(prix_par_type.index, rotation=45, ha='right')
            ax.set_title("Prix moyen par type de bien (FCFA)", fontsize=14, fontweight='bold')
            ax.set_ylabel("Prix moyen (FCFA)", fontsize=12)
            
            # Ajout des valeurs sur les barres
            for bar, val in zip(bars, prix_par_type['Prix_Demande'].values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + bar.get_height()*0.02,
                       f'{int(val):,}', ha='center', fontweight='bold', fontsize=10)
            
            # Formatage des axes en entiers
            ax = format_axis_integer(ax)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Affichage du tableau
            st.subheader("Détail par type de bien")
            df_display = prix_par_type.copy()
            for col in ['Prix_Demande', 'Prix_M2']:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(lambda x: f"{int(x):,} FCFA" if col == 'Prix_Demande' else f"{int(x):,} FCFA/m²")
            df_display['Surface'] = df_display['Surface'].apply(lambda x: f"{int(x):.0f} m²")
            st.dataframe(df_display, use_container_width=True)

# ============================================
# SECTION 3: CORRÉLATIONS
# ============================================
elif page == " Corrélations":
    if df.empty:
        st.warning(" Aucune donnée disponible.")
    else:
        st.header(" Analyse des corrélations")
        
        st.markdown("""
        Cette matrice montre comment les différentes caractéristiques du bien 
        influencent le prix. 
        - **Couleurs chaudes (rouges)** : corrélation positive
        - **Couleurs froides (bleues)** : corrélation négative
        """)
        
        cols_numeriques = ['Surface', 'Nombre_Pieces', 'Nombre_Chambres', 'Nombre_SDB',
                          'Annee_Construction', 'Prix_Demande', 'Prix_M2']
        
        cols_disponibles = [col for col in cols_numeriques if col in df.columns]
        corr_matrix = df[cols_disponibles].corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='RdBu_r', 
                   center=0, fmt='.2f', square=True, ax=ax,
                   cbar_kws={"shrink": 0.8})
        ax.set_title("Matrice des corrélations - Facteurs influençant le prix", fontsize=14, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        
        st.markdown("---")
        st.subheader(" Interprétation des corrélations avec le prix")
        
        if 'Prix_Demande' in corr_matrix.columns:
            corr_prix = corr_matrix['Prix_Demande'].drop('Prix_Demande').sort_values(ascending=False)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("** Facteurs qui augmentent le prix**")
                facteurs_positifs = False
                for var, corr in corr_prix.items():
                    if corr > 0.1:
                        st.write(f"• **{var}**: {corr:.3f}")
                        facteurs_positifs = True
                if not facteurs_positifs:
                    st.info("Aucun facteur avec corrélation positive significative (> 0.1)")
            
            with col2:
                st.markdown("** Facteurs qui diminuent le prix**")
                facteurs_negatifs = False
                for var, corr in corr_prix.items():
                    if corr < -0.1:
                        st.write(f"• **{var}**: {corr:.3f}")
                        facteurs_negatifs = True
                if not facteurs_negatifs:
                    st.info("Aucun facteur avec corrélation négative significative (< -0.1)")
        
        # Corrélation avec le prix au m²
        st.markdown("---")
        st.subheader(" Facteurs influençant le prix au m²")
        if 'Prix_M2' in corr_matrix.columns and 'Prix_M2' in corr_matrix.index:
            corr_m2 = corr_matrix['Prix_M2'].drop('Prix_M2').sort_values(ascending=False)
            for var, corr in corr_m2.items():
                if abs(corr) > 0.1:
                    st.write(f"• **{var}**: {corr:.3f}")
            if not any(abs(c) > 0.1 for c in corr_m2.values):
                st.info("Aucun facteur avec corrélation significative (> 0.1 en valeur absolue)")
