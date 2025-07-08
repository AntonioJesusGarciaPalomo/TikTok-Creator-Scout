// frontend/src/components/FilterPanel.js
import React, { useState } from 'react';
import { X, Filter, RefreshCw, Download, Search } from 'lucide-react';

const FilterPanel = ({
    isOpen,
    onClose,
    onApplyFilters,
    segments,
    initialFilters = {},
    onExport,
    onRefresh
}) => {
    const [filters, setFilters] = useState({
        minFollowers: '',
        maxFollowers: '',
        minEngagement: '',
        minPostingFrequency: '',
        minGrowthRate: '',
        segment: '',
        search: '',
        ...initialFilters
    });

    const [showAdvanced, setShowAdvanced] = useState(false);

    const handleInputChange = (field, value) => {
        setFilters(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleReset = () => {
        setFilters({
            minFollowers: '',
            maxFollowers: '',
            minEngagement: '',
            minPostingFrequency: '',
            minGrowthRate: '',
            segment: '',
            search: ''
        });
    };

    const handleApply = () => {
        // Filtrar valores vacíos
        const activeFilters = Object.entries(filters).reduce((acc, [key, value]) => {
            if (value !== '') {
                acc[key] = value;
            }
            return acc;
        }, {});

        onApplyFilters(activeFilters);
    };

    // Presets de filtros rápidos
    const applyPreset = (preset) => {
        switch (preset) {
            case 'high-potential':
                setFilters({
                    ...filters,
                    minEngagement: '5',
                    minGrowthRate: '10',
                    minPostingFrequency: '3'
                });
                break;
            case 'micro-influencers':
                setFilters({
                    ...filters,
                    minFollowers: '10000',
                    maxFollowers: '100000',
                    minEngagement: '3'
                });
                break;
            case 'rising-stars':
                setFilters({
                    ...filters,
                    segment: 'Rising Stars',
                    minGrowthRate: '20'
                });
                break;
            case 'consistent':
                setFilters({
                    ...filters,
                    segment: 'Consistent Performers',
                    minPostingFrequency: '5'
                });
                break;
            default:
                break;
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-end">
            <div className="bg-white w-full max-w-md h-full overflow-y-auto shadow-2xl">
                {/* Header */}
                <div className="sticky top-0 bg-white border-b px-6 py-4">
                    <div className="flex justify-between items-center">
                        <h2 className="text-xl font-bold text-gray-900">Filtros</h2>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                            <X className="h-5 w-5 text-gray-500" />
                        </button>
                    </div>
                </div>

                {/* Contenido */}
                <div className="p-6">
                    {/* Búsqueda */}
                    <div className="mb-6">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Buscar Creador
                        </label>
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <input
                                type="text"
                                value={filters.search}
                                onChange={(e) => handleInputChange('search', e.target.value)}
                                placeholder="Nombre o @username"
                                className="pl-10 w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                    </div>

                    {/* Filtros Rápidos */}
                    <div className="mb-6">
                        <h3 className="text-sm font-medium text-gray-700 mb-3">Filtros Rápidos</h3>
                        <div className="grid grid-cols-2 gap-2">
                            <button
                                onClick={() => applyPreset('high-potential')}
                                className="px-3 py-2 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
                            >
                                Alto Potencial
                            </button>
                            <button
                                onClick={() => applyPreset('micro-influencers')}
                                className="px-3 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                            >
                                Micro-influencers
                            </button>
                            <button
                                onClick={() => applyPreset('rising-stars')}
                                className="px-3 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                            >
                                Rising Stars
                            </button>
                            <button
                                onClick={() => applyPreset('consistent')}
                                className="px-3 py-2 text-sm bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors"
                            >
                                Consistentes
                            </button>
                        </div>
                    </div>

                    {/* Filtros Principales */}
                    <div className="space-y-4 mb-6">
                        {/* Seguidores */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Rango de Seguidores
                            </label>
                            <div className="grid grid-cols-2 gap-2">
                                <input
                                    type="number"
                                    value={filters.minFollowers}
                                    onChange={(e) => handleInputChange('minFollowers', e.target.value)}
                                    placeholder="Mínimo"
                                    className="rounded-lg border-gray-300 shadow-sm"
                                />
                                <input
                                    type="number"
                                    value={filters.maxFollowers}
                                    onChange={(e) => handleInputChange('maxFollowers', e.target.value)}
                                    placeholder="Máximo"
                                    className="rounded-lg border-gray-300 shadow-sm"
                                />
                            </div>
                        </div>

                        {/* Engagement */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Engagement Mínimo (%)
                            </label>
                            <input
                                type="number"
                                step="0.1"
                                value={filters.minEngagement}
                                onChange={(e) => handleInputChange('minEngagement', e.target.value)}
                                placeholder="Ej: 2.5"
                                className="w-full rounded-lg border-gray-300 shadow-sm"
                            />
                        </div>

                        {/* Segmento */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Segmento
                            </label>
                            <select
                                value={filters.segment}
                                onChange={(e) => handleInputChange('segment', e.target.value)}
                                className="w-full rounded-lg border-gray-300 shadow-sm"
                            >
                                <option value="">Todos los segmentos</option>
                                {Object.keys(segments).map(segment => (
                                    <option key={segment} value={segment}>{segment}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Filtros Avanzados */}
                    <div className="mb-6">
                        <button
                            onClick={() => setShowAdvanced(!showAdvanced)}
                            className="flex items-center text-sm font-medium text-blue-600 hover:text-blue-800"
                        >
                            {showAdvanced ? 'Ocultar' : 'Mostrar'} filtros avanzados
                            <svg
                                className={`ml-1 h-4 w-4 transform transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>

                        {showAdvanced && (
                            <div className="mt-4 space-y-4">
                                {/* Frecuencia de Publicación */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Frecuencia Mínima (videos/semana)
                                    </label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        value={filters.minPostingFrequency}
                                        onChange={(e) => handleInputChange('minPostingFrequency', e.target.value)}
                                        placeholder="Ej: 3"
                                        className="w-full rounded-lg border-gray-300 shadow-sm"
                                    />
                                </div>

                                {/* Tasa de Crecimiento */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Crecimiento Semanal Mínimo (%)
                                    </label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        value={filters.minGrowthRate}
                                        onChange={(e) => handleInputChange('minGrowthRate', e.target.value)}
                                        placeholder="Ej: 5"
                                        className="w-full rounded-lg border-gray-300 shadow-sm"
                                    />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Acciones Adicionales */}
                    <div className="border-t pt-4 mb-6">
                        <div className="flex gap-2">
                            {onRefresh && (
                                <button
                                    onClick={onRefresh}
                                    className="flex-1 flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                                >
                                    <RefreshCw className="h-4 w-4 mr-2" />
                                    Actualizar
                                </button>
                            )}
                            {onExport && (
                                <button
                                    onClick={onExport}
                                    className="flex-1 flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                                >
                                    <Download className="h-4 w-4 mr-2" />
                                    Exportar
                                </button>
                            )}
                        </div>
                    </div>
                </div>

                {/* Footer con botones */}
                <div className="sticky bottom-0 bg-white border-t px-6 py-4">
                    <div className="flex gap-3">
                        <button
                            onClick={handleReset}
                            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                            Limpiar
                        </button>
                        <button
                            onClick={handleApply}
                            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            Aplicar Filtros
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FilterPanel;