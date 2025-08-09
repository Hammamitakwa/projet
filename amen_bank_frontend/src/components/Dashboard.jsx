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
  const [recentTransactions, setRecentTransactions] = useState([])
  const [selectedAccount, setSelectedAccount] = useState(null)
  const [showTransactions, setShowTransactions] = useState(false)

  useEffect(() => {
    fetchAccounts()
    fetchRecentTransactions()
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

  const fetchRecentTransactions = async () => {
    try {
      // Récupérer les transactions de tous les comptes
      const response = await fetch('/api/accounts', {
        credentials: 'include'
      })
      const data = await response.json()
      
      if (data.accounts && data.accounts.length > 0) {
        // Récupérer les transactions du premier compte pour commencer
        const firstAccount = data.accounts[0]
        const transResponse = await fetch(`/api/accounts/${firstAccount.account_id}/transactions?limit=10`, {
          credentials: 'include'
        })
        const transData = await transResponse.json()
        setRecentTransactions(transData.transactions || [])
      }
    } catch (error) {
      console.error('Erreur lors du chargement des transactions:', error)
    }
  }

  const fetchAccountTransactions = async (accountId) => {
    try {
      const response = await fetch(`/api/accounts/${accountId}/transactions?limit=20`, {
        credentials: 'include'
      })
      const data = await response.json()
      return data.transactions || []
    } catch (error) {
      console.error('Erreur lors du chargement des transactions du compte:', error)
      return []
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
                {recentTransactions.length > 0 ? (
                  <>
                    <div className="text-xl font-semibold">
                      {showBalances ? formatCurrency(recentTransactions[0].amount) : '••••••'}
                    </div>
                    <p className="text-green-100 text-sm mt-1">
                      {recentTransactions[0].description} • {recentTransactions[0].transaction_date}
                    </p>
                  </>
                ) : (
                  <>
                    <div className="text-xl font-semibold">---</div>
                    <p className="text-green-100 text-sm mt-1">Aucune transaction récente</p>
                  </>
                )}
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

        {/* Section des transactions récentes */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900">Transactions Récentes</h3>
            <Button 
              variant="outline" 
              className="rounded-full"
              onClick={() => {
                if (accounts.length > 0) {
                  fetchAccountTransactions(accounts[0].account_id).then(transactions => {
                    setSelectedAccount({...accounts[0], transactions})
                    setShowTransactions(true)
                  })
                }
              }}
            >
              Voir tout
            </Button>
          </div>

          <Card className="border-gray-200">
            <CardContent className="p-6">
              {recentTransactions.length > 0 ? (
                <div className="space-y-4">
                  {recentTransactions.slice(0, 5).map((transaction) => (
                    <div key={transaction.transaction_id} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          transaction.debit_credit_indicator === 'D' 
                            ? 'bg-red-100 text-red-600' 
                            : 'bg-green-100 text-green-600'
                        }`}>
                          {transaction.debit_credit_indicator === 'D' ? 
                            <ArrowDownLeft className="h-4 w-4" /> : 
                            <ArrowUpRight className="h-4 w-4" />
                          }
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 text-sm">{transaction.description}</p>
                          <p className="text-xs text-gray-600">{transaction.transaction_date}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`font-semibold text-sm ${
                          transaction.debit_credit_indicator === 'D' 
                            ? 'text-red-600' 
                            : 'text-green-600'
                        }`}>
                          {transaction.debit_credit_indicator === 'D' ? '-' : '+'}
                          {showBalances ? formatCurrency(transaction.amount) : '••••••'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Aucune transaction récente</p>
                  <p className="text-sm text-gray-500 mt-1">Vos dernières transactions apparaîtront ici</p>
                </div>
              )}
            </CardContent>
          </Card>
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
                      onClick={async () => {
                        const transactions = await fetchAccountTransactions(account.account_id)
                        setSelectedAccount({...account, transactions})
                        setShowTransactions(true)
                      }}
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

        {/* Modal pour afficher les transactions */}
        {showTransactions && selectedAccount && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">
                      Historique des transactions
                    </h3>
                    <p className="text-gray-600">
                      {selectedAccount.account_label} • {selectedAccount.account_number}
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => setShowTransactions(false)}
                    className="rounded-full"
                  >
                    Fermer
                  </Button>
                </div>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                {selectedAccount.transactions && selectedAccount.transactions.length > 0 ? (
                  <div className="space-y-4">
                    {selectedAccount.transactions.map((transaction) => (
                      <div key={transaction.transaction_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            transaction.debit_credit_indicator === 'D' 
                              ? 'bg-red-100 text-red-600' 
                              : 'bg-green-100 text-green-600'
                          }`}>
                            {transaction.debit_credit_indicator === 'D' ? 
                              <ArrowDownLeft className="h-5 w-5" /> : 
                              <ArrowUpRight className="h-5 w-5" />
                            }
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{transaction.description}</p>
                            <p className="text-sm text-gray-600">
                              {transaction.transaction_date} • {transaction.transaction_type}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className={`font-semibold ${
                            transaction.debit_credit_indicator === 'D' 
                              ? 'text-red-600' 
                              : 'text-green-600'
                          }`}>
                            {transaction.debit_credit_indicator === 'D' ? '-' : '+'}
                            {formatCurrency(transaction.amount)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Aucune transaction trouvée pour ce compte</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

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
