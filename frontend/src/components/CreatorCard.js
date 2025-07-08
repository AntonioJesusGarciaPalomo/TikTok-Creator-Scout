// frontend/src/components/CreatorCard.js
import React from 'react';
import { TrendingUp, Users, Activity, Calendar } from 'lucide-react';

const CreatorCard = ({ creator, onClick, segmentColors }) => {
    return (
        <div
            className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 p-6 cursor-pointer"
            onClick={() => onClick(creator)}
        >
            {/* Header con Avatar y Info Básica */}
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                    <img
                        className="h-12 w-12 rounded-full ring-2 ring-gray-200"
                        src={creator.avatar_url || `https://ui-avatars.com/api/?name=${creator.username}`}
                        alt={creator.username}
                    />
                    <div className="ml-3">
                        <h3 className="text-lg font-semibold text-gray-900">
                            {creator.display_name}
                        </h3>
                        <p className="text-sm text-gray-500">@{creator.username}</p>
                    </div>
                </div>
                {creator.verified && (
                    <span className="text-blue-500 text-sm font-medium">✓ Verificado</span>
                )}
            </div>

            {/* Bio */}
            {creator.bio && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {creator.bio}
                </p>
            )}

            {/* Métricas Grid */}
            <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center">
                        <Users className="h-4 w-4 text-blue-500 mr-2" />
                        <div>
                            <p className="text-xs text-gray-600">Seguidores</p>
                            <p className="text-sm font-bold text-gray-900">
                                {creator.followers_count >= 1000000
                                    ? `${(creator.followers_count / 1000000).toFixed(1)}M`
                                    : creator.followers_count >= 1000
                                        ? `${(creator.followers_count / 1000).toFixed(1)}K`
                                        : creator.followers_count.toLocaleString()
                                }
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center">
                        <Activity className="h-4 w-4 text-purple-500 mr-2" />
                        <div>
                            <p className="text-xs text-gray-600">Engagement</p>
                            <p className="text-sm font-bold text-gray-900">
                                {creator.engagement_rate.toFixed(2)}%
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center">
                        <TrendingUp className="h-4 w-4 text-green-500 mr-2" />
                        <div>
                            <p className="text-xs text-gray-600">Crecimiento</p>
                            <p className={`text-sm font-bold ${creator.growth_rate > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {creator.growth_rate > 0 ? '+' : ''}{creator.growth_rate.toFixed(1)}%
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center">
                        <Calendar className="h-4 w-4 text-orange-500 mr-2" />
                        <div>
                            <p className="text-xs text-gray-600">Frecuencia</p>
                            <p className="text-sm font-bold text-gray-900">
                                {creator.posting_frequency.toFixed(1)}/sem
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Score de Potencial */}
            <div className="mb-4">
                <div className="flex justify-between items-center mb-1">
                    <span className="text-xs font-medium text-gray-600">Score de Potencial</span>
                    <span className="text-xs font-bold text-gray-900">{creator.potential_score.toFixed(0)}/100</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                        className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${creator.potential_score}%` }}
                    ></div>
                </div>
            </div>

            {/* Segmento */}
            <div className="flex justify-between items-center">
                <span
                    className="px-3 py-1 text-xs font-semibold rounded-full"
                    style={{
                        backgroundColor: `${segmentColors[creator.segment]}20`,
                        color: segmentColors[creator.segment]
                    }}
                >
                    {creator.segment}
                </span>

                <button
                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    onClick={(e) => {
                        e.stopPropagation();
                        onClick(creator);
                    }}
                >
                    Ver más →
                </button>
            </div>

            {/* Badge de Rendimiento */}
            {creator.potential_score >= 80 && (
                <div className="absolute top-2 right-2">
                    <span className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-white text-xs px-2 py-1 rounded-full font-bold">
                        ⭐ TOP
                    </span>
                </div>
            )}
        </div>
    );
};

export default CreatorCard;