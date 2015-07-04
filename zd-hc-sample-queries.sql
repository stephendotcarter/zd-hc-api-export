\pset pager off

-- Total Articles
SELECT COUNT(*) as articles FROM articles;

-- Total Categories
SELECT COUNT(*) as categories FROM categories;

-- Total Sections
SELECT COUNT(*) as sections FROM sections;

-- Total Sections per Category
SELECT c.name, COUNT(*) as sections FROM categories c, sections s WHERE c.id = s.category_id GROUP BY c.name ORDER BY c.name;

-- Total Articles per Section per Category
SELECT c.name as category_name, s.name as section_name, COUNT(*) as total FROM categories c, sections s, articles a WHERE c.id = s.category_id AND s.id = a.section_id GROUP BY c.name, s.name ORDER BY c.name, s.name;

-- Articles per Section per Category Top 10
SELECT c.name as category_name, COUNT(*) as articles FROM categories c, sections s, articles a WHERE c.id = s.category_id AND s.id = a.section_id GROUP BY c.name ORDER BY articles DESC LIMIT 10;

-- Articles per Section per Category Top 10
SELECT c.name as category_name, s.name as section_name, COUNT(*) as articles FROM categories c, sections s, articles a WHERE c.id = s.category_id AND s.id = a.section_id GROUP BY c.name, s.name ORDER BY articles DESC LIMIT 10;

-- Articles per User Top 10
SELECT u.name as user_name, COUNT(*) as articles FROM users u, articles a WHERE u.id = a.author_id GROUP BY u.name ORDER BY articles DESC LIMIT 10;

-- Translations created in past week
SELECT t.created_at as translation_created_at, t.title as translation_title FROM translations t WHERE t.created_at > (CURRENT_DATE - INTERVAL '1 week') ORDER BY t.created_at;

-- Translations updated in past week
SELECT t.updated_at as translation_updated_at, t.title as translation_title FROM articles a, translations t WHERE a.id = t.source_id AND a.created_at < (CURRENT_DATE - INTERVAL '1 week') AND t.updated_at > (CURRENT_DATE - INTERVAL '1 week') ORDER BY t.updated_at;
