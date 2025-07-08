import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Search, Filter, TrendingUp, Users, Activity, Calendar, ChevronDown, X } from 'lucide-react';
import api from '../services/api';

const Dashboard = () => {
    const [creators, setCreators] = useState([]);
    const [segments, setSegments] = useState({});
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        minFollowers: '',
        minEngagement: '',
        minPostingFrequency: '',
        minGrowthRate: '',
        segment: ''
    });
    const [showFilters, setShowFilters] = useState(false);
    const [selectedCreator, setSelectedCreator] = useState(null);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            // Fetch creators
            const creatorsData = await api.getCreators();
            setCreators(creatorsData);

            // Fetch segments summary
            const segmentsData = await api.getSegmentsSummary();
            setSegments(segmentsData);
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setLoading(false);
        }
    };

    const applyFilters = async () => {
        try {
            const data = await api.getCreators(filters);
            setCreators(data);
            setShowFilters(false);
        } catch (error) {
            console.error('Error applying filters:', error);
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
                <div className="text-2xl text-gray-600">Cargando datos...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100">
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-6">
                        <h1 className="text-3xl font-bold text-gray-900">TikTok Creator Scout</h1>
                        <button
                            onClick={() => setShowFilters(!showFilters)}
                            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                        >
                            <Filter className="mr-2 h-4 w-4" />
                            Filtros
                        </button>
                    </div>
                </div>
            </header>

            {/* Filters Panel */}
            {showFilters && (
                <div className="bg-white shadow-lg absolute right-0 top-20 w-96 z-10 rounded-lg m-4 p-6">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-medium">Filtros</h3>
                        <button onClick={() => setShowFilters(false)}>
                            <X className="h-5 w-5 text-gray-500" />
                        </button>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Min. Seguidores</label>
                            <input
                                type="number"
                                value={filters.minFollowers}
                                onChange={(e) => setFilters({ ...filters, minFollowers: e.target.value })}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">Min. Engagement (%)</label>
                            <input
                                type="number"
                                step="0.1"
                                value={filters.minEngagement}
                                onChange={(e) => setFilters({ ...filters, minEngagement: e.target.value })}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">Min. Frecuencia (videos/semana)</label>
                            <input
                                type="number"
                                step="0.1"
                                value={filters.minPostingFrequency}
                                onChange={(e) => setFilters({ ...filters, minPostingFrequency: e.target.value })}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">Min. Tasa Crecimiento (%)</label>
                            <input
                                type="number"
                                step="0.1"
                                value={filters.minGrowthRate}
                                onChange={(e) => setFilters({ ...filters, minGrowthRate: e.target.value })}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">Segmento</label>
                            <select
                                value={filters.segment}
                                onChange={(e) => setFilters({ ...filters, segment: e.target.value })}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                            >
                                <option value="">Todos</option>
                                {Object.keys(segments).map(segment => (
                                    <option key={segment} value={segment}>{segment}</option>
                                ))}
                            </select>
                        </div>

                        <button
                            onClick={applyFilters}
                            className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                        >
                            Aplicar Filtros
                        </button>
                    </div>
                </div>
            )}

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
                                    {(creators.reduce((acc, c) => acc + c.growth_rate, 0) / creators.length).toFixed(1)}%
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
                                    {(creators.reduce((acc, c) => acc + c.engagement_rate, 0) / creators.length).toFixed(2)}%
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
                                    {(creators.reduce((acc, c) => acc + c.posting_frequency, 0) / creators.length).toFixed(1)} /sem
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

                {/* Creators Table */}
                <div className="bg-white shadow rounded-lg">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-medium text-gray-900">Lista de Creadores</h3>
                    </div>
                    <div className="overflow-x-auto">
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
                </div>
            </main>

            {/* Creator Modal */}
            {selectedCreator && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
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
                            <button onClick={() => setSelectedCreator(null)}>
                                <X className="h-6 w-6 text-gray-500" />
                            </button>
                        </div>

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

                        <div className="space-y-4">
                            <div>
                                <p className="text-sm text-gray-600">Tasa de Engagement</p>
                                <div className="flex items-center">
                                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-blue-500 h-2 rounded-full"
                                            style={{ width: `${Math.min(selectedCreator.engagement_rate * 10, 100)}%` }}
                                        ></div>
                                    </div>
                                    <span className="ml-2 font-medium">{selectedCreator.engagement_rate.toFixed(2)}%</span>
                                </div>
                            </div>

                            <div>
                                <p className="text-sm text-gray-600">Crecimiento Semanal</p>
                                <div className="flex items-center">
                                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                                        <div
                                            className={`h-2 rounded-full ${selectedCreator.growth_rate > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                                            style={{ width: `${Math.min(Math.abs(selectedCreator.growth_rate) * 5, 100)}%` }}
                                        ></div>
                                    </div>
                                    <span className={`ml-2 font-medium ${selectedCreator.growth_rate > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {selectedCreator.growth_rate > 0 ? '+' : ''}{selectedCreator.growth_rate.toFixed(1)}%
                                    </span>
                                </div>
                            </div>

                            <div>
                                <p className="text-sm text-gray-600">Score de Potencial</p>
                                <div className="flex items-center">
                                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-purple-500 h-2 rounded-full"
                                            style={{ width: `${selectedCreator.potential_score}%` }}
                                        ></div>
                                    </div>
                                    <span className="ml-2 font-medium">{selectedCreator.potential_score.toFixed(0)}/100</span>
                                </div>
                            </div>
                        </div>

                        <div className="mt-6 pt-6 border-t">
                            <div className="grid grid-cols-3 gap-4 text-center">
                                <div>
                                    <p className="text-sm text-gray-600">Promedio Likes</p>
                                    <p className="text-xl font-bold">{Math.round(selectedCreator.avg_likes_per_video).toLocaleString()}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600">Promedio Comentarios</p>
                                    <p className="text-xl font-bold">{Math.round(selectedCreator.avg_comments_per_video).toLocaleString()}</p>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600">Frecuencia</p>
                                    <p className="text-xl font-bold">{selectedCreator.posting_frequency.toFixed(1)} /sem</p>
                                </div>
                            </div>
                        </div>

                        <div className="mt-6">
                            <span className={`px-4 py-2 text-sm font-semibold rounded-full`}
                                style={{
                                    backgroundColor: `${segmentColors[selectedCreator.segment]}20`,
                                    color: segmentColors[selectedCreator.segment]
                                }}>
                                {selectedCreator.segment}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;