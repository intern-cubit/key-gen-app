import React, { useState, useEffect } from 'react'
import axios from 'axios'

// Check if we're running in Electron or regular browser
const isElectron = typeof window !== 'undefined' && window.process && window.process.type
const API_BASE_URL = 'http://localhost:8001'

function App() {
  const [activeTab, setActiveTab] = useState('generate')
  const [activations, setActivations] = useState([])
  const [loading, setLoading] = useState(false)
  
  // Generate Key Form State
  const [systemId, setSystemId] = useState('')
  const [appName, setAppName] = useState('wa-bomb')
  const [customerName, setCustomerName] = useState('')
  const [customerMobile, setCustomerMobile] = useState('')
  const [customerEmail, setCustomerEmail] = useState('')
  const [validityDays, setValidityDays] = useState('')
  const [isLifetime, setIsLifetime] = useState(true)
  const [generatedKey, setGeneratedKey] = useState('')
  
  // Verify Key Form State
  const [verifySystemId, setVerifySystemId] = useState('')
  const [verifyAppName, setVerifyAppName] = useState('wa-bomb')
  const [verifyActivationKey, setVerifyActivationKey] = useState('')
  const [verificationResult, setVerificationResult] = useState(null)
  
  // Customer Stats State
  const [customerStatsEmail, setCustomerStatsEmail] = useState('')
  const [customerStats, setCustomerStats] = useState(null)

  useEffect(() => {
    if (activeTab === 'manage') {
      fetchActivations()
    }
  }, [activeTab])

  const fetchActivations = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/get-all-keys`)
      setActivations(response.data.activations)
    } catch (error) {
      console.error('Error fetching activations:', error)
      alert('Error fetching activations')
    } finally {
      setLoading(false)
    }
  }

  const generateKey = async (e) => {
    e.preventDefault()
    try {
      setLoading(true)
      const payload = {
        system_id: systemId,
        app_name: appName,
        customer_name: customerName,
        customer_mobile: customerMobile,
        customer_email: customerEmail
      }
      
      // Only include validity_days if not lifetime
      if (!isLifetime && validityDays) {
        payload.validity_days = parseInt(validityDays)
      }
      
      const response = await axios.post(`${API_BASE_URL}/generate-key`, payload)
      
      setGeneratedKey(response.data.activation_key)
      alert('Activation key generated successfully!')
    } catch (error) {
      console.error('Error generating key:', error)
      alert('Error generating activation key')
    } finally {
      setLoading(false)
    }
  }

  const verifyKey = async (e) => {
    e.preventDefault()
    try {
      setLoading(true)
      const response = await axios.post(`${API_BASE_URL}/verify-key`, {
        system_id: verifySystemId,
        activation_key: verifyActivationKey,
        app_name: verifyAppName
      })
      
      setVerificationResult(response.data)
    } catch (error) {
      console.error('Error verifying key:', error)
      alert('Error verifying activation key')
    } finally {
      setLoading(false)
    }
  }

  const deactivateKey = async (activationKey) => {
    if (!confirm('Are you sure you want to deactivate this key?')) return
    
    try {
      setLoading(true)
      const formData = new FormData()
      formData.append('activation_key', activationKey)
      
      await axios.post(`${API_BASE_URL}/deactivate-key`, formData)
      alert('Key deactivated successfully!')
      fetchActivations()
    } catch (error) {
      console.error('Error deactivating key:', error)
      alert('Error deactivating key')
    } finally {
      setLoading(false)
    }
  }

  const fetchCustomerStats = async (e) => {
    e.preventDefault()
    if (!customerStatsEmail.trim()) return
    
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE_URL}/customer-stats/${encodeURIComponent(customerStatsEmail)}`)
      setCustomerStats(response.data.stats)
    } catch (error) {
      console.error('Error fetching customer stats:', error)
      alert('Error fetching customer statistics')
      setCustomerStats(null)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString || dateString === "Never expires") {
      return "Never expires"
    }
    return new Date(dateString).toLocaleDateString()
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          Multi-App Activation Key Manager
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Generate and manage activation keys for wa-bomb and mail-storm applications
        </p>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="flex space-x-1 bg-white p-1 rounded-lg shadow">
            <button
              onClick={() => setActiveTab('generate')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'generate'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Generate Key
            </button>
            <button
              onClick={() => setActiveTab('verify')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'verify'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Verify Key
            </button>
            <button
              onClick={() => setActiveTab('manage')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'manage'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Manage Keys
            </button>
            <button
              onClick={() => setActiveTab('customer-stats')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'customer-stats'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Customer Stats
            </button>
          </div>
        </div>

        {/* Generate Key Tab */}
        {activeTab === 'generate' && (
          <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Generate Activation Key</h2>
            <form onSubmit={generateKey}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  App Name *
                </label>
                <select
                  value={appName}
                  onChange={(e) => setAppName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="wa-bomb">wa-bomb</option>
                  <option value="mail-storm">mail-storm</option>
                </select>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  System ID *
                </label>
                <input
                  type="text"
                  value={systemId}
                  onChange={(e) => setSystemId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  placeholder="Enter system ID"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Customer Name *
                </label>
                <input
                  type="text"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter customer name"
                  required
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mobile Number
                </label>
                <input
                  type="tel"
                  value={customerMobile}
                  onChange={(e) => setCustomerMobile(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter mobile number"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <input
                  type="email"
                  value={customerEmail}
                  onChange={(e) => setCustomerEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter email address"
                  required
                />
              </div>
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Key Validity
                </label>
                <div className="space-y-3">
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="lifetime"
                      name="validity"
                      checked={isLifetime}
                      onChange={() => setIsLifetime(true)}
                      className="mr-2"
                    />
                    <label htmlFor="lifetime" className="text-sm font-medium text-gray-700">
                      Lifetime (Never expires)
                    </label>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="limited"
                      name="validity"
                      checked={!isLifetime}
                      onChange={() => setIsLifetime(false)}
                      className="mr-2"
                    />
                    <label htmlFor="limited" className="text-sm font-medium text-gray-700">
                      Limited time
                    </label>
                  </div>
                  
                  {!isLifetime && (
                    <div className="ml-6">
                      <input
                        type="number"
                        value={validityDays}
                        onChange={(e) => setValidityDays(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        min="1"
                        placeholder="Enter validity in days"
                        required={!isLifetime}
                      />
                    </div>
                  )}
                </div>
              </div>
              
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Generating...' : 'Generate Key'}
              </button>
            </form>
            
            {generatedKey && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
                <h3 className="font-semibold text-green-800 mb-2">Generated Key:</h3>
                <p className="font-mono text-lg text-green-700 bg-white p-2 rounded border">
                  {generatedKey}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Verify Key Tab */}
        {activeTab === 'verify' && (
          <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Verify Activation Key</h2>
            <form onSubmit={verifyKey}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Application *
                </label>
                <select
                  value={verifyAppName}
                  onChange={(e) => setVerifyAppName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="wa-bomb">wa-bomb</option>
                  <option value="mail-storm">mail-storm</option>
                </select>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  System ID *
                </label>
                <input
                  type="text"
                  value={verifySystemId}
                  onChange={(e) => setVerifySystemId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  placeholder="Enter system ID"
                />
              </div>
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Activation Key *
                </label>
                <input
                  type="text"
                  value={verifyActivationKey}
                  onChange={(e) => setVerifyActivationKey(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  placeholder="Enter activation key"
                />
              </div>
              
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
              >
                {loading ? 'Verifying...' : 'Verify Key'}
              </button>
            </form>
            
            {verificationResult && (
              <div className={`mt-6 p-4 rounded-md ${
                verificationResult.valid 
                  ? 'bg-green-50 border border-green-200' 
                  : 'bg-red-50 border border-red-200'
              }`}>
                <h3 className={`font-semibold mb-2 ${
                  verificationResult.valid ? 'text-green-800' : 'text-red-800'
                }`}>
                  Verification Result:
                </h3>
                <p className={`${
                  verificationResult.valid ? 'text-green-700' : 'text-red-700'
                }`}>
                  {verificationResult.message}
                </p>
                {verificationResult.valid && (
                  <div className="mt-2 text-sm text-green-600">
                    {verificationResult.customer_name && (
                      <p>Customer: {verificationResult.customer_name}</p>
                    )}
                    {verificationResult.expires_at && (
                      <p>Expires: {formatDate(verificationResult.expires_at)}</p>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Manage Keys Tab */}
        {activeTab === 'manage' && (
          <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Manage Activation Keys</h2>
              <button
                onClick={fetchActivations}
                disabled={loading}
                className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">App</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">System ID</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Activation Key</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Customer Name</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Mobile</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Email</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Created</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Expires</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Status</th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {activations.map((activation, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-2 text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          activation.app_name === 'wa-bomb'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-purple-100 text-purple-800'
                        }`}>
                          {activation.app_name}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-sm font-mono">{activation.system_id}</td>
                      <td className="px-4 py-2 text-sm font-mono">{activation.activation_key}</td>
                      <td className="px-4 py-2 text-sm">{activation.customer_name || 'N/A'}</td>
                      <td className="px-4 py-2 text-sm">{activation.customer_mobile || 'N/A'}</td>
                      <td className="px-4 py-2 text-sm">{activation.customer_email || 'N/A'}</td>
                      <td className="px-4 py-2 text-sm">{formatDate(activation.created_at)}</td>
                      <td className="px-4 py-2 text-sm">{formatDate(activation.expires_at)}</td>
                      <td className="px-4 py-2 text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          activation.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {activation.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-sm">
                        {activation.is_active && (
                          <button
                            onClick={() => deactivateKey(activation.activation_key)}
                            className="text-red-600 hover:text-red-800 text-sm"
                          >
                            Deactivate
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {activations.length === 0 && !loading && (
                <div className="text-center py-8 text-gray-500">
                  No activation keys found
                </div>
              )}
            </div>
          </div>
        )}

        {/* Customer Statistics Tab */}
        {activeTab === 'customer-stats' && (
          <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Customer Statistics</h2>
            
            <form onSubmit={fetchCustomerStats} className="mb-6">
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Customer Email Address
                  </label>
                  <input
                    type="email"
                    value={customerStatsEmail}
                    onChange={(e) => setCustomerStatsEmail(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter customer email"
                    required
                  />
                </div>
                <div className="flex items-end">
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-500 text-white py-2 px-6 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {loading ? 'Loading...' : 'Get Stats'}
                  </button>
                </div>
              </div>
            </form>

            {customerStats && (
              <div className="space-y-6">
                {/* Customer Info */}
                {customerStats.customer_info && customerStats.customer_info.name && (
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-blue-800 mb-2">Customer Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Name:</span> {customerStats.customer_info.name}
                      </div>
                      <div>
                        <span className="font-medium">Mobile:</span> {customerStats.customer_info.mobile || 'N/A'}
                      </div>
                      <div>
                        <span className="font-medium">Email:</span> {customerStats.customer_info.email}
                      </div>
                    </div>
                  </div>
                )}

                {/* Overall Statistics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-green-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-green-600">{customerStats.total_keys}</div>
                    <div className="text-sm text-green-700">Total Keys</div>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-600">{customerStats.active_keys}</div>
                    <div className="text-sm text-blue-700">Active Keys</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-yellow-600">{customerStats.expired_keys}</div>
                    <div className="text-sm text-yellow-700">Expired Keys</div>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-red-600">{customerStats.deactivated_keys}</div>
                    <div className="text-sm text-red-700">Deactivated Keys</div>
                  </div>
                </div>

                {/* App-wise Statistics */}
                <div>
                  <h3 className="font-semibold text-gray-800 mb-3">App-wise Breakdown</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(customerStats.apps).map(([appName, appStats]) => (
                      <div key={appName} className="border rounded-lg p-4">
                        <h4 className="font-medium text-gray-700 mb-3 capitalize">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            appName === 'wa-bomb' 
                              ? 'bg-blue-100 text-blue-800' 
                              : 'bg-purple-100 text-purple-800'
                          }`}>
                            {appName}
                          </span>
                        </h4>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>Total: <span className="font-medium">{appStats.total}</span></div>
                          <div>Active: <span className="font-medium text-green-600">{appStats.active}</span></div>
                          <div>Expired: <span className="font-medium text-yellow-600">{appStats.expired}</span></div>
                          <div>Deactivated: <span className="font-medium text-red-600">{appStats.deactivated}</span></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Activation History */}
                {customerStats.activations && customerStats.activations.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-800 mb-3">Activation History</h3>
                    <div className="overflow-x-auto">
                      <table className="min-w-full table-auto text-sm">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-3 py-2 text-left font-medium text-gray-700">App</th>
                            <th className="px-3 py-2 text-left font-medium text-gray-700">Key</th>
                            <th className="px-3 py-2 text-left font-medium text-gray-700">Created</th>
                            <th className="px-3 py-2 text-left font-medium text-gray-700">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {customerStats.activations.map((activation, index) => (
                            <tr key={index} className="hover:bg-gray-50">
                              <td className="px-3 py-2">
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  activation.app_name === 'wa-bomb'
                                    ? 'bg-blue-100 text-blue-800'
                                    : 'bg-purple-100 text-purple-800'
                                }`}>
                                  {activation.app_name}
                                </span>
                              </td>
                              <td className="px-3 py-2 font-mono">{activation.activation_key}</td>
                              <td className="px-3 py-2">{formatDate(activation.created_at)}</td>
                              <td className="px-3 py-2">
                                <span className={`px-2 py-1 rounded-full text-xs ${
                                  activation.is_active
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-red-100 text-red-800'
                                }`}>
                                  {activation.is_active ? 'Active' : 'Inactive'}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}

            {customerStats === null && customerStatsEmail && (
              <div className="text-center py-8 text-gray-500">
                No data found for the provided email address
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App