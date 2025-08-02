import { useState, useEffect } from 'react'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { ChatInterface } from './ChatInterface'
import { 
  CreditCard, 
  TrendingUp, 
  ArrowUpRight, 
  ArrowDownLeft, 
  Plus,
  MessageCircle,
  Eye,
  EyeOff,
  Wallet,
  PiggyBank,
  Building,
  Calendar,
  DollarSign,
  Activity
} from 'lucide-react'
import amenLogo from '../assets/amen_bank.jpeg'

export function Dashboard({ user, onLogout }) {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showBalances, setShowBalances] = useState(true)
  const [isChatOpen, setIsChatOpen] = useState(false)

  useEffect(() => {
    fetchAccounts()
  }, [])

  const fetchAccounts = async () => {
    try {
      const response = await fetch('/api/accounts', {
        credentials: 'include'
      })
      const data = await response.json()
      setAccounts(data.accounts || [])
    } catch (error) {
      console.error('Erreur lors du chargement des comptes:', error)
    } finally {
      setLoading(false)
    }
  }

  const getTotalBalance = () => {
    return accounts.reduce((total, account) => total + account.current_balance, 0)
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-TN', {
      style: 'currency',
      currency: 'TND',
      minimumFractionDigits: 3
    }).format(amount).replace('TND', 'DT')
  }

  const getAccountIcon = (accountType) => {
    switch (accountType?.toLowerCase()) {
      case 'courant':
        return <Wallet className="h-5 w-5" />
      case 'épargne':
        return <PiggyBank className="h-5 w-5" />
      case 'entreprise':
        return <Building className="h-5 w-5" />
      default:
        return <CreditCard className="h-5 w-5" />
    }
  }

  const getBalanceColor = (balance) => {
    if (balance > 0) return 'text-green-600'
    if (balance < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  const getBalanceIcon = (balance) => {
    if (balance > 0) return <TrendingUp className="h-4 w-4 text-green-500" />
    if (balance < 0) return <ArrowDownLeft className="h-4 w-4 text-red-500" />
    return <Activity className="h-4 w-4 text-gray-500" />
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto"></div>
          <p className="text-gray-600">Chargement de vos comptes...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header moderne */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo et titre */}
            <div className="flex items-center gap-4">
              <div className="relative">
                <img 
                  src={amenLogo} 
                  alt="Amen Bank" 
                  className="h-10 w-10 rounded-full object-cover ring-2 ring-blue-100"
                />
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
                  Amen Bank
                </h1>
                <p className="text-sm text-gray-600">Services Bancaires en Ligne</p>
              </div>
            </div>

            {/* Actions utilisateur */}
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Bienvenue, {user.full_name}</p>
                <p className="text-xs text-gray-500">{user.username}</p>
              </div>
              
              <Button
                onClick={() => setIsChatOpen(true)}
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-full px-6"
              >
                <MessageCircle className="h-4 w-4 mr-2" />
                Assistant IA
              </Button>
              
              <Button
                variant="outline"
                onClick={onLogout}
                className="rounded-full border-gray-300 hover:border-gray-400"
              >
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Contenu principal */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Vue d'ensemble */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Vue d'ensemble de vos comptes</h2>
              <p className="text-gray-600">Gérez vos finances avec notre assistant IA intelligent</p>
            </div>
            <Button
              variant="outline"
              onClick={() => setShowBalances(!showBalances)}
              className="rounded-full"
            >
              {showBalances ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
              {showBalances ? 'Masquer' : 'Afficher'}
            </Button>
          </div>

          {/* Cartes de résumé */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Solde total */}
            <Card className="bg-gradient-to-br from-blue-600 to-blue-700 text-white border-0 shadow-lg">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg font-medium flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  Solde Total
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {showBalances ? formatCurrency(getTotalBalance()) : '••••••'}
                </div>
                <p className="text-blue-100 text-sm mt-1">
                  {accounts.length} compte{accounts.length > 1 ? 's' : ''} actif{accounts.length > 1 ? 's' : ''}
                </p>
              </CardContent>
            </Card>

            {/* Dernière transaction */}
            <Card className="bg-gradient-to-br from-green-600 to-green-700 text-white border-0 shadow-lg">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg font-medium flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Dernière Transaction
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xl font-semibold">---</div>
                <p className="text-green-100 text-sm mt-1">Aucune transaction récente</p>
              </CardContent>
            </Card>

            {/* Statut */}
            <Card className="bg-gradient-to-br from-purple-600 to-purple-700 text-white border-0 shadow-lg">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg font-medium flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Statut
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <Badge className="bg-green-500 text-white border-0">Actif</Badge>
                </div>
                <p className="text-purple-100 text-sm mt-1">Tous les services disponibles</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Liste des comptes */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold text-gray-900">Mes Comptes</h3>
            <Button variant="outline" className="rounded-full">
              <Plus className="h-4 w-4 mr-2" />
              Nouveau compte
            </Button>
          </div>

          <div className="grid gap-6">
            {accounts.map((account) => (
              <Card key={account.account_id} className="hover:shadow-lg transition-all duration-200 border-gray-200">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center">
                        {getAccountIcon(account.account_type)}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 text-lg">{account.account_label}</h4>
                        <p className="text-gray-600 text-sm">N° {account.account_number} • {account.account_type?.toUpperCase() || 'COURANT'}</p>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="flex items-center gap-2 justify-end mb-1">
                        {getBalanceIcon(account.current_balance)}
                        <span className="text-sm text-gray-600">Solde actuel</span>
                      </div>
                      <div className={`text-2xl font-bold ${getBalanceColor(account.current_balance)}`}>
                        {showBalances ? formatCurrency(account.current_balance) : '••••••'}
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-3 mt-6">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1 rounded-full border-blue-200 text-blue-700 hover:bg-blue-50"
                    >
                      <ArrowUpRight className="h-4 w-4 mr-2" />
                      Virer
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1 rounded-full border-green-200 text-green-700 hover:bg-green-50"
                    >
                      <TrendingUp className="h-4 w-4 mr-2" />
                      Historique
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Bouton d'action flottant pour l'assistant */}
        <div className="fixed bottom-6 right-6 z-30">
          <Button
            onClick={() => setIsChatOpen(true)}
            className="w-14 h-14 rounded-full bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 shadow-lg hover:shadow-xl transition-all duration-200"
          >
            <MessageCircle className="h-6 w-6" />
          </Button>
        </div>
      </main>

      {/* Interface de chat */}
      <ChatInterface 
        isOpen={isChatOpen} 
        onClose={() => setIsChatOpen(false)} 
        user={user}
      />
    </div>
  )
}

