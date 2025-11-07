import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Search, Filter, TrendingUp, Users, Activity, Calendar, Grid, List, Plus, X } from 'lucide-react';
import api from '../services/api';
import CreatorCard from './CreatorCard';
import FilterPanel from './FilterPanel';

const Dashboard = () => {
    const [creators, setCreators] = useState([]);
    const [segments, setSegments] = useState({});
    const [loading, setLoading] = useState(true);
    const [showFilters, setShowFilters] = useState(false);
    const [selectedCreator, setSelectedCreator] = useState(null);
    const [viewMode, setViewMode] = useState('grid'); // 'grid' o 'table'
    const [showAddCreator, setShowAddCreator] = useState(false);
    const [newCreatorUsername, setNewCreatorUsername] = useState('');
    const [scraping, setScraping] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const creatorsData = await api.getCreators();
            setCreators(creatorsData);

            const segmentsData = await api.getSegmentsSummary();
            setSegments(segmentsData);
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleApplyFilters = async (filters) => {
        try {
            const data = await api.getCreators(filters);
            setCreators(data);
            setShowFilters(false);
        } catch (error) {
            console.error('Error applying filters:', error);
        }
    };

    const handleExport = () => {
        // Implementar exportación a CSV
        const csv = creators.map(c => ({
            username: c.username,
            followers: c.followers_count,
            engagement: c.engagement_rate,
            growth: c.growth_rate,
            segment: c.segment,
            score: c.potential_score
        }));

        console.log('Exportando datos...', csv);
        // Aquí implementarías la descarga real del CSV
    };

    const handleAddCreator = async () => {
        if (!newCreatorUsername) return;

        try {
            setScraping(true);
            await api.scrapeCreator(newCreatorUsername);
            setNewCreatorUsername('');
            setShowAddCreator(false);
            await fetchData(); // Recargar datos
        } catch (error) {
            console.error('Error scraping creator:', error);
            alert('Error al agregar creador. Verifica el username.');
        } finally {
            setScraping(false);
        }
    };

    const segmentColors = {
        'Rising Stars': '#8B5CF6',
        'Consistent Performers': '#3B82F6',
        'High Engagement': '#10B981',
        'Growth Needed': '#F59E0B',
        'Emerging Talent': '#EC4899'
    };

    const segmentData = Object.entries(segments).map(([name, data]) => ({
        name,
        value: data.count,
        avgFollowers: Math.round(data.avg_followers),
        avgEngagement: data.avg_engagement.toFixed(2)
    }));

    const topCreators = [...creators]
        .sort((a, b) => b.potential_score - a.potential_score)
        .slice(0, 10);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Cargando datos...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100">
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-6">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">TikTok Creator Scout</h1>
                            <p className="text-sm text-gray-500 mt-1">
                                Monitorea y analiza creadores con potencial
                            </p>
                        </div>
                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => setShowAddCreator(true)}
                                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                            >
                                <Plus className="mr-2 h-4 w-4" />
                                Agregar Creador
                            </button>
                            <button
                                onClick={() => setShowFilters(true)}
                                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                            >
                                <Filter className="mr-2 h-4 w-4" />
                                Filtros
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Filter Panel */}
            <FilterPanel
                isOpen={showFilters}
                onClose={() => setShowFilters(false)}
                onApplyFilters={handleApplyFilters}
                segments={segments}
                onExport={handleExport}
                onRefresh={fetchData}
            />

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="flex items-center">
                            <Users className="h-10 w-10 text-blue-500" />
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-600">Total Creadores</p>
                                <p className="text-2xl font-bold text-gray-900">{creators.length}</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="flex items-center">
                            <TrendingUp className="h-10 w-10 text-green-500" />
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-600">Crecimiento Promedio</p>
                                <p className="text-2xl font-bold text-gray-900">
                                    {creators.length > 0 ? (creators.reduce((acc, c) => acc + c.growth_rate, 0) / creators.length).toFixed(1) : '0.0'}%
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="flex items-center">
                            <Activity className="h-10 w-10 text-purple-500" />
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-600">Engagement Promedio</p>
                                <p className="text-2xl font-bold text-gray-900">
                                    {creators.length > 0 ? (creators.reduce((acc, c) => acc + c.engagement_rate, 0) / creators.length).toFixed(2) : '0.00'}%
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="flex items-center">
                            <Calendar className="h-10 w-10 text-orange-500" />
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-600">Frecuencia Promedio</p>
                                <p className="text-2xl font-bold text-gray-900">
                                    {creators.length > 0 ? (creators.reduce((acc, c) => acc + c.posting_frequency, 0) / creators.length).toFixed(1) : '0.0'} /sem
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Segments Distribution */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Distribución por Segmentos</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={segmentData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                >
                                    {segmentData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={segmentColors[entry.name] || '#8884d8'} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Top Creators by Potential Score */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Top 10 Creadores por Potencial</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={topCreators}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="username" angle={-45} textAnchor="end" height={80} />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="potential_score" fill="#8B5CF6" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* View Mode Toggle */}
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-medium text-gray-900">
                        Creadores ({creators.length})
                    </h3>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setViewMode('grid')}
                            className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400'}`}
                        >
                            <Grid className="h-5 w-5" />
                        </button>
                        <button
                            onClick={() => setViewMode('table')}
                            className={`p-2 rounded ${viewMode === 'table' ? 'bg-blue-100 text-blue-600' : 'text-gray-400'}`}
                        >
                            <List className="h-5 w-5" />
                        </button>
                    </div>
                </div>

                {/* Creators View */}
                {viewMode === 'grid' ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {creators.map((creator) => (
                            <CreatorCard
                                key={creator.id}
                                creator={creator}
                                onClick={setSelectedCreator}
                                segmentColors={segmentColors}
                            />
                        ))}
                    </div>
                ) : (
                    /* Table View */
                    <div className="bg-white shadow rounded-lg overflow-hidden">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Creador
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Seguidores
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Engagement
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Crecimiento
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Frecuencia
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Segmento
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Score
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {creators.map((creator) => (
                                    <tr
                                        key={creator.id}
                                        className="hover:bg-gray-50 cursor-pointer"
                                        onClick={() => setSelectedCreator(creator)}
                                    >
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <img
                                                    className="h-10 w-10 rounded-full"
                                                    src={creator.avatar_url || `https://ui-avatars.com/api/?name=${creator.username}`}
                                                    alt=""
                                                />
                                                <div className="ml-4">
                                                    <div className="text-sm font-medium text-gray-900">
                                                        {creator.display_name}
                                                    </div>
                                                    <div className="text-sm text-gray-500">
                                                        @{creator.username}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {creator.followers_count.toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {creator.engagement_rate.toFixed(2)}%
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`text-sm ${creator.growth_rate > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                {creator.growth_rate > 0 ? '+' : ''}{creator.growth_rate.toFixed(1)}%
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {creator.posting_frequency.toFixed(1)} /sem
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full`}
                                                style={{
                                                    backgroundColor: `${segmentColors[creator.segment]}20`,
                                                    color: segmentColors[creator.segment]
                                                }}>
                                                {creator.segment}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            <div className="flex items-center">
                                                <div className="w-16 bg-gray-200 rounded-full h-2">
                                                    <div
                                                        className="bg-green-500 h-2 rounded-full"
                                                        style={{ width: `${creator.potential_score}%` }}
                                                    ></div>
                                                </div>
                                                <span className="ml-2">{creator.potential_score.toFixed(0)}</span>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </main>

            {/* Add Creator Modal */}
            {showAddCreator && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full">
                        <h3 className="text-lg font-medium mb-4">Agregar Nuevo Creador</h3>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Username de TikTok
                            </label>
                            <input
                                type="text"
                                value={newCreatorUsername}
                                onChange={(e) => setNewCreatorUsername(e.target.value)}
                                placeholder="@username (sin @)"
                                className="w-full rounded-lg border-gray-300 shadow-sm"
                                disabled={scraping}
                            />
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => {
                                    setShowAddCreator(false);
                                    setNewCreatorUsername('');
                                }}
                                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                disabled={scraping}
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleAddCreator}
                                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                                disabled={scraping || !newCreatorUsername}
                            >
                                {scraping ? 'Agregando...' : 'Agregar'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Creator Modal - Detalles */}
            {selectedCreator && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        {/* Contenido del modal igual que antes */}
                        <div className="flex justify-between items-start mb-6">
                            <div className="flex items-center">
                                <img
                                    className="h-20 w-20 rounded-full"
                                    src={selectedCreator.avatar_url || `https://ui-avatars.com/api/?name=${selectedCreator.username}`}
                                    alt=""
                                />
                                <div className="ml-4">
                                    <h2 className="text-2xl font-bold">{selectedCreator.display_name}</h2>
                                    <p className="text-gray-500">@{selectedCreator.username}</p>
                                    {selectedCreator.verified && (
                                        <span className="text-blue-500 text-sm">✓ Verificado</span>
                                    )}
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedCreator(null)}
                                className="p-2 hover:bg-gray-100 rounded-lg"
                            >
                                <X className="h-6 w-6 text-gray-500" />
                            </button>
                        </div>

                        {/* Resto del contenido del modal... */}
                        <div className="mb-6">
                            <p className="text-gray-700">{selectedCreator.bio}</p>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="bg-gray-50 p-4 rounded-lg">
                                <p className="text-sm text-gray-600">Seguidores</p>
                                <p className="text-2xl font-bold">{selectedCreator.followers_count.toLocaleString()}</p>
                            </div>
                            <div className="bg-gray-50 p-4 rounded-lg">
                                <p className="text-sm text-gray-600">Total Likes</p>
                                <p className="text-2xl font-bold">{selectedCreator.likes_count.toLocaleString()}</p>
                            </div>
                            <div className="bg-gray-50 p-4 rounded-lg">
                                <p className="text-sm text-gray-600">Videos</p>
                                <p className="text-2xl font-bold">{selectedCreator.videos_count}</p>
                            </div>
                            <div className="bg-gray-50 p-4 rounded-lg">
                                <p className="text-sm text-gray-600">Siguiendo</p>
                                <p className="text-2xl font-bold">{selectedCreator.following_count}</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;