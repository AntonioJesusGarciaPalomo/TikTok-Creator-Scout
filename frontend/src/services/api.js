const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const GRAPHQL_URL = process.env.REACT_APP_GRAPHQL_URL || 'http://localhost:8000/graphql';

class ApiService {
    // Métodos para REST API
    async getCreators(filters = {}) {
        const queryParams = new URLSearchParams();
        Object.keys(filters).forEach(key => {
            if (filters[key]) {
                queryParams.append(key.replace(/([A-Z])/g, '_$1').toLowerCase(), filters[key]);
            }
        });

        const response = await fetch(`${API_URL}/creators?${queryParams}`);
        if (!response.ok) throw new Error('Error fetching creators');
        return response.json();
    }

    async getCreator(username) {
        const response = await fetch(`${API_URL}/creators/${username}`);
        if (!response.ok) throw new Error('Creator not found');
        return response.json();
    }

    async getSegmentsSummary() {
        const response = await fetch(`${API_URL}/creators/segments/summary`);
        if (!response.ok) throw new Error('Error fetching segments');
        return response.json();
    }

    // Métodos para GraphQL
    async graphqlQuery(query, variables = {}) {
        const response = await fetch(GRAPHQL_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query,
                variables,
            }),
        });

        const result = await response.json();
        if (result.errors) {
            throw new Error(result.errors[0].message);
        }
        return result.data;
    }

    // Scraping
    async scrapeCreator(username) {
        const mutation = `
      mutation ScrapeCreator($username: String!) {
        scrapeCreator(username: $username) {
          id
          username
          displayName
          followersCount
          engagementRate
          potentialScore
        }
      }
    `;

        return this.graphqlQuery(mutation, { username });
    }

    async batchScrapeCreators(usernames) {
        const mutation = `
      mutation BatchScrape($usernames: [String!]!) {
        batchScrape(usernames: $usernames) {
          id
          username
          displayName
          followersCount
          engagementRate
          potentialScore
        }
      }
    `;

        return this.graphqlQuery(mutation, { usernames });
    }

    // Análisis avanzado
    async getSegmentAnalysis() {
        const query = `
      query {
        segmentAnalysis {
          segmentName
          creatorCount
          avgFollowers
          avgEngagement
          avgGrowth
          aiInsights
        }
      }
    `;

        return this.graphqlQuery(query);
    }
}

export default new ApiService();