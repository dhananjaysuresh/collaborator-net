'''
Created on Mar 17, 2016

@author: DJ
'''
import click, csv
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError
from py2neo import authenticate, Graph
from py2neo.cypher import CypherError

try:
    click.echo('Connecting to MongoDB server.............')
    client = MongoClient('localhost', 27017)
    client.server_info()
except ServerSelectionTimeoutError as err:
    click.echo(err)
    click.echo('Connection failed, exiting!')
    exit()
    
try:
    click.echo('Connecting to Neo4j server.............')
    authenticate("localhost:7474", "neo4j", "pass")
    graph = Graph()
    click.echo(graph.neo4j_version)
except:
    click.echo("Error connecting to Neo4j")
    exit()

db = client.collaborator_database
#db.users_collection.drop()
#db.organization_distances.drop()
graph_constraints = {"User" : "user_id", "Skill" : "name",
                     "Interest" : "name", "Organization" : "name",
                     "Project" : "name"}

for k in graph_constraints:
    try:
        graph.schema.create_uniqueness_constraint(k, graph_constraints[k])
    except:
        pass

@click.group()
def main():
    pass

@click.command('load_users', short_help='Load CSV file with users')
@click.argument('filename', type=click.Path(exists=True))
def load_users(filename):
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f, fieldnames=['user_id', 'first_name', 'last_name', 'phone', 'address', 'degree'])
        db.users.create_index([('user_id', ASCENDING)], unique=True)
        for row in reader:
            try:
                user_id = db.users.insert_one(row).inserted_id
                click.echo('Inserted user with id: {0}'.format(user_id))
            except DuplicateKeyError as err:
                click.echo('Duplicate key entered')
            
            cypher = graph.cypher
            try:
                record = cypher.execute("CREATE (user:User {user_id:{a}, first_name:{b}, last_name:{c}}) RETURN user",
                               a=row['user_id'], b=row['first_name'], c=row['last_name'])
                click.echo(record.one)
            except CypherError as err:
                click.echo(err)
            
@click.command('load_user_organizations', short_help='Load CSV file with users and their organization')
@click.argument('filename', type=click.Path(exists=True))
def load_user_organizations(filename):
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f, fieldnames=['user_id', 'organization', 'organization_type'])
        for row in reader:
            write_result = db.users.update({'user_id' : row['user_id']},
                                                      {'$set':
                                                       {'organization' :
                                                        {'name' : row['organization'], 'type' : row['organization_type']}
                                                        }
                                                       }
                                                      )
            click.echo('Inserted user organization with result: {0}'.format(write_result))
            
            cypher = graph.cypher
            try:
                record = cypher.execute("CREATE (org:Organization {name:{a}, type:{b}})",
                                        a=row['organization'], b=row['organization_type'])
                click.echo(record.one)
            except CypherError as err:
                click.echo(err)
            try:
                record = cypher.execute("MATCH (user:User {user_id:{id}}), (org:Organization {name:{a}})\n" +
                                        "CREATE UNIQUE (user)-[rel:IN]->(org) RETURN rel",
                                        a=row['organization'], id=row['user_id'])
                click.echo(record.one)
            except CypherError as err:
                click.echo(err)
            
@click.command('load_user_projects', short_help='Load CSV file with users and their projects')
@click.argument('filename', type=click.Path(exists=True))
def load_user_projects(filename):
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f, fieldnames=['user_id', 'project'])
        for row in reader:
            write_result = db.user.update({'user_id' : row['user_id']},
                                                      {'$push':
                                                       {'projects' :
                                                        {'name' : row['project']}
                                                        }
                                                       }
                                                      )
            click.echo('Inserted user project with result: {0}'.format(write_result))
            
            cypher = graph.cypher
            try:
                record = cypher.execute("CREATE (proj:Project {name:{a}})", a=row['project'])
                click.echo(record.one)
            except CypherError as err:
                click.echo(err)
            try:
                record = cypher.execute("MATCH (user:User {user_id:{id}}), (proj:Project {name:{a}})\n" +
                                        "CREATE UNIQUE (user)-[rel:WORKS_ON]->(proj) RETURN rel",
                                        a=row['project'], id=row['user_id'])
                click.echo(record.one)
            except CypherError as err:
                click.echo(err)
            
@click.command('load_user_skills', short_help='Load CSV file with users and their skills')
@click.argument('filename', type=click.Path(exists=True))
def load_user_skills(filename):
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f, fieldnames=['user_id', 'skill', 'skill_level'])
        for row in reader:
            try:
                row['skill_level'] = int(float(row['skill_level']))
            except ValueError:
                continue
            write_result = db.users.update({'user_id' : row['user_id']},
                                                      {'$push':
                                                       {'skills' :
                                                        {'name' : row['skill'], 'level' : row['skill_level']}
                                                        }
                                                       }
                                                      )
            click.echo('Inserted user skill with result: {0}'.format(write_result))
            
            cypher = graph.cypher
            try:
                record = cypher.execute("CREATE (skill:Skill {name:{a}})", a=row['skill'])
                click.echo(record.one)
            except CypherError as err:
                click.echo(err)
            try:
                record = cypher.execute("MATCH (user:User {user_id:{id}}), (skill:Skill {name:{a}})\n" +
                                        "CREATE UNIQUE (user)-[rel:KNOWS {level:{b}}]->(skill) RETURN rel",
                                        a=row['skill'], b=row['skill_level'], id=row['user_id'])
                click.echo(record.one)
            except CypherError as err:
                click.echo(err)
            
@click.command('load_user_interests', short_help='Load CSV file with users and their interests')
@click.argument('filename', type=click.Path(exists=True))
def load_user_interests(filename):
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f, fieldnames=['user_id', 'interest', 'interest_level'])
        for row in reader:
            try:
                row['interest_level'] = int(float(row['interest_level']))
            except ValueError:
                continue
            write_result = db.users.update({'user_id' : row['user_id']},
                                                      {'$push':
                                                       {'interests' :
                                                        {'name' : row['interest'], 'level' : row['interest_level']}
                                                        }
                                                       }
                                                      )
            click.echo('Inserted user interest with result: {0}'.format(write_result))
            
            cypher = graph.cypher
            try:
                record = cypher.execute("CREATE (interest:Interest {name:{a}})", a=row['interest'])
                click.echo(record.one)
            except CypherError as err:
                click.echo(err)
            try:
                record = cypher.execute("MATCH (user:User {user_id:{id}}), (interest:Interest {name:{a}})\n" +
                                        "CREATE UNIQUE (user)-[rel:LIKES {level:{b}}]->(interest) RETURN rel",
                                        a=row['interest'], b=row['interest_level'], id=row['user_id'])
                click.echo(record.one)
            except CypherError as err:
                click.echo(err)
            
@click.command('load_organization_distances', short_help='Load CSV file organizations and their distances')
@click.argument('filename', type=click.Path(exists=True))
def load_organization_distances(filename):
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f, fieldnames=['organization_1', 'organization_2', 'distance'])
        for row in reader:
            try:
                row['distance'] = int(float(row['distance']))
            except ValueError:
                continue
            user_id = db.organization_distances.insert_one(row).inserted_id
            click.echo('Inserted organization distances with id: {0}'.format(user_id))
            try:
                cypher = graph.cypher
                record = cypher.execute("MATCH (org1:Organization {name:{a}}), (org2:Organization {name:{b}})\n"+
                                        "CREATE UNIQUE (org1)-[rel:DISTANCE_FROM {distance:{c}}]->(org2) RETURN rel",
                                        a=row['organization_1'], b=row['organization_2'], c=row['distance'])
                click.echo(record.one)
            except CypherError as err:
                click.echo(err)
            
@click.command('get_user', short_help='Get user by user id')
@click.argument('user_id')
def get_user(user_id):
    user = db.users.find({'user_id' : user_id})
    template = '{0:10}|{1:15}|{2:15}|{3:10}|{4:30}|{5:15}'
    header = template.format('User Id', 'First Name', 'Last Name', 'Phone', 'Address', 'Degree')
    click.echo(header)
    click.echo('-'*len(header))
    for document in user:
        click.echo(template.format(document['user_id'], document['first_name'], document['last_name'], document['phone'], document['address'], document['degree']))
        
@click.command('get_similar_users', short_help='Get similar users')
@click.argument('user_id')
def get_similar_users(user_id):
    try:
        cypher = graph.cypher
        record = cypher.execute("MATCH (user:User {user_id:{id}})-[:LIKES]->(likes)<-[knows_b:LIKES]-(related_user:User)," +
                                "(user)-[:IN]->(user_org)<-[dis:DISTANCE_FROM]-(nearby_org)\n" +
                                "WHERE dis.distance<=10\n" +
                                "WITH user, knows_b, related_user, nearby_org, likes\n" +
                                "MATCH (related_user)-[:IN]-(nearby_org)\n" +
                                "RETURN DISTINCT user, knows_b.level, likes.name, related_user, labels(likes)\n" +
                                "ORDER BY knows_b.level DESC", id=user_id)
    except CypherError as err:
        click.echo(err)
        exit()
        
    click.echo("Related users to {0}".format(user_id))
    template = '{0:10}|{1:15}|{2:15}|{3:10}|{4:10}|{5:4}'
    header = template.format('User Id', 'First Name', 'Last Name', 'Type','Attribute', 'Level')
    click.echo(header)
    click.echo('-'*len(header))
    for document in record:
        related_user = document['related_user']
        click.echo(template.format(related_user['user_id'], related_user['first_name'], related_user['last_name'], document['labels(likes)'][0], document['likes.name'], document['knows_b.level']))
            
@click.command('get_trusted_colleagues', short_help='Get trusted colleagues-of-colleagues')
@click.argument('user_id')
def get_trusted_colleagues(user_id):
    try:
        cypher = graph.cypher
        record = cypher.execute("MATCH (user:User {user_id:{id}}), " +
                                "(u1:User)-[:WORKS_ON]->(projects)<-[:WORKS_ON]-(u2:User), " +
                                "(u1)-[:LIKES]-(interests)\n" +
                                "WITH user, u1, u2, projects, collect(interests.name) as i\n" +
                                "WHERE u1.user_id <> user.user_id AND u2.user_id <> user.user_id AND u1 <> u2\n" +
                                "RETURN DISTINCT u1, i", id=user_id)
    except CypherError as err:
        click.echo(err)
        exit()
        
    click.echo("Trusted Colleagues:")
    template = '{0:10}|{1:15}|{2:15}|{3:10}'
    header = template.format('User Id', 'First Name', 'Last Name', 'Interest')
    click.echo(header)
    click.echo('-'*len(header))
    for document in record:
        colleague = document['u1']
        interests = document['i']
        click.echo(template.format(colleague['user_id'], colleague['first_name'], colleague['last_name'], interests[0]))
        for i in range(1,len(interests)):
            click.echo(template.format("", "", "", interests[i]))

main.add_command(load_users)
main.add_command(load_user_organizations)
main.add_command(load_user_projects)
main.add_command(load_user_skills)  
main.add_command(load_user_interests)  
main.add_command(load_organization_distances)
main.add_command(get_user)
main.add_command(get_similar_users)
main.add_command(get_trusted_colleagues)

if __name__ == '__main__':
    main()
        

