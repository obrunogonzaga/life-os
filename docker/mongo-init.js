// MongoDB initialization script for Life OS
print('🚀 Inicializando banco de dados Life OS...');

// Conectar ao banco lifeos
db = db.getSiblingDB('lifeos');

// Criar usuário específico para a aplicação
db.createUser({
  user: 'lifeos_app',
  pwd: 'lifeos_app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'lifeos'
    }
  ]
});

// Criar coleções com esquemas básicos
db.createCollection('news_articles');
db.createCollection('news_metadata');
db.createCollection('article_details');

// Criar índices para performance
print('📊 Criando índices...');

// Índices para news_articles
db.news_articles.createIndex({ "link": 1 }, { unique: true });
db.news_articles.createIndex({ "origem": 1 });
db.news_articles.createIndex({ "data_scraping": -1 });
db.news_articles.createIndex({ "titulo": 1 });

// Índices para news_metadata
db.news_metadata.createIndex({ "origem": 1 }, { unique: true });
db.news_metadata.createIndex({ "ultimo_update": -1 });

// Índices para article_details
db.article_details.createIndex({ "link": 1 }, { unique: true });
db.article_details.createIndex({ "data_scraping": -1 });
db.article_details.createIndex({ "ultimo_acesso": -1 });
db.article_details.createIndex({ 
  "data_scraping": 1 
}, { 
  expireAfterSeconds: 432000  // 5 dias = 5 * 24 * 60 * 60 segundos
});

// Inserir documento inicial de configuração
db.news_metadata.insertOne({
  _id: 'config',
  created_at: new Date(),
  version: '1.0.0',
  description: 'Life OS News System Configuration'
});

print('✅ Banco de dados Life OS inicializado com sucesso!');
print('📝 Usuário criado: lifeos_app');
print('🗂️  Coleções criadas: news_articles, news_metadata, article_details');
print('📊 Índices criados para performance otimizada');
print('🕒 TTL configurado: article_details expiram em 5 dias');