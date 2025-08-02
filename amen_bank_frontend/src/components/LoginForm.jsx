import { useState } from 'react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Label } from './ui/label'
import { Alert, AlertDescription } from './ui/alert'
import { LogIn, Eye, EyeOff, Sparkles, Shield, Zap } from 'lucide-react'
import amenLogo from '../assets/amen_bank.jpeg'

export function LoginForm({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      // Appel à votre API Flask
      const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important pour les sessions Flask
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (response.ok) {
        // Connexion réussie
        onLogin(data.user)
      } else {
        // Erreur de connexion
        setError(data.error || 'Erreur de connexion')
      }
    } catch (err) {
      console.error('Erreur de connexion:', err)
      // Vérifier si c'est un problème de CORS ou de connexion
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Impossible de se connecter au serveur. Vérifiez que le serveur Flask est démarré.')
      } else {
        setError('Erreur de connexion au serveur')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Arrière-plan moderne avec gradients */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-green-50"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(0,102,204,0.1),transparent_50%)]"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(0,204,102,0.1),transparent_50%)]"></div>
      
      {/* Éléments décoratifs flottants */}
      <div className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-blue-200/30 to-blue-300/30 rounded-full blur-xl animate-pulse"></div>
      <div className="absolute bottom-20 right-20 w-40 h-40 bg-gradient-to-br from-green-200/30 to-green-300/30 rounded-full blur-xl animate-pulse delay-1000"></div>
      
      <div className="relative z-10 w-full max-w-md animate-fade-in-up">
        {/* Carte de connexion moderne */}
        <Card className="modern-card glass-effect border-0 shadow-xl">
          <CardHeader className="text-center space-y-6 pb-8">
            {/* Logo avec effet moderne */}
            <div className="flex justify-center">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-green-500/20 rounded-full blur-lg"></div>
                <img 
                  src={amenLogo} 
                  alt="Amen Bank" 
                  className="relative h-20 w-20 rounded-full object-cover ring-4 ring-white shadow-lg"
                />
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-br from-green-400 to-green-500 rounded-full flex items-center justify-center">
                  <Sparkles className="h-3 w-3 text-white" />
                </div>
              </div>
            </div>
            
            {/* Titre avec gradient */}
            <div className="space-y-2">
              <CardTitle className="text-3xl font-bold gradient-text">
                Amen Bank
              </CardTitle>
              <CardDescription className="text-base text-gray-600">
                Votre banque digitale nouvelle génération
              </CardDescription>
            </div>
            
            {/* Badges de fonctionnalités */}
            <div className="flex justify-center gap-4 text-xs">
              <div className="flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-700 rounded-full">
                <Shield className="h-3 w-3" />
                <span>Sécurisé</span>
              </div>
              <div className="flex items-center gap-1 px-3 py-1 bg-green-50 text-green-700 rounded-full">
                <Zap className="h-3 w-3" />
                <span>IA Intégrée</span>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Champ nom d'utilisateur */}
              <div className="space-y-2">
                <Label htmlFor="username" className="text-sm font-medium text-gray-700">
                  Nom d'utilisateur
                </Label>
                <Input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Entrez votre nom d'utilisateur"
                  className="modern-input h-12"
                  required
                />
              </div>
              
              {/* Champ mot de passe */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Mot de passe
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Entrez votre mot de passe"
                    className="modern-input h-12 pr-12"
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-12 px-3 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-500" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-500" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Message d'erreur */}
              {error && (
                <Alert variant="destructive" className="animate-scale-in">
                  <AlertDescription className="text-sm">{error}</AlertDescription>
                </Alert>
              )}

              {/* Bouton de connexion */}
              <Button 
                type="submit" 
                className="modern-button modern-button-primary w-full h-12 text-base font-semibold"
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                    <span>Connexion en cours...</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <LogIn className="h-5 w-5" />
                    <span>Se connecter</span>
                  </div>
                )}
              </Button>
            </form>
            
            {/* Informations de démonstration */}
            <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg border border-blue-100">
              <div className="text-center space-y-2">
                <p className="text-sm font-medium text-gray-700">
                  🚀 Compte de test
                </p>
                <div className="space-y-1 text-xs text-gray-600">
                  <p>Utilisez vos identifiants de base de données</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Connectez-vous avec votre compte utilisateur
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Footer moderne */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>© 2025 Amen Bank - Banque digitale intelligente</p>
        </div>
      </div>
    </div>
  )
}