// Path: frontend/utils/export.ts

export function triggerBackendDownload(format: 'csv' | 'json') {
    const config = useRuntimeConfig()
    const BACKEND_URL = config.public.backendUrl
    
    // Créer l'URL de l'API de téléchargement
    const url = `${BACKEND_URL}/api/telecharger/${format}`;

    // Créer un lien temporaire pour simuler le téléchargement
    const link = document.createElement('a');
    link.href = url;
    
    // Le nom du fichier sera géré par les headers du Backend, mais on met un fallback
    link.setAttribute('download', `citations_${new Date().toISOString().split('T')[0]}.${format}`); 
    document.body.appendChild(link);
    
    // Simuler le clic pour démarrer le téléchargement
    link.click();
    
    // Nettoyer le lien temporaire
    document.body.removeChild(link);
}