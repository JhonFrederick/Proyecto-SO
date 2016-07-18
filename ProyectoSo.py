#!flask/bin/python
from flask import Flask, jsonify, make_response,request
import subprocess

app = Flask(__name__)

# Web service que se invoca al momento de ejecutar el comando
# curl http://localhost:5000

@app.route('/',methods = ['GET'])
def index():
	return "Proyecto SO "

# Este metodo retorna la lista de sistemas operativos soportados por VirtualBox
# Los tipos de sistemas operativos soportados deben ser mostrados al ejecutar 
# como invocar: curl http://localhost:5000/vms/ostypes
@app.route('/vms/ostypes',methods = ['GET'])
def ostypes():
	output = subprocess.check_output(['VBoxManage','list','ostypes']) + "\n"
	return output

# Este metodo retorna la lista de maquinas asociadas con un usuario al ejecutar
# como invocar: curl http://localhost:5000/vms
@app.route('/vms',methods = ['GET'])
def listvms():
	output = subprocess.check_output(['VBoxManage','list','vms'])
	return output

# Este metodo retorna aquellas maquinas que se encuentran en ejecucion al 
# como invocar: curl http://localhost:5000/vms/running
@app.route('/vms/running',methods = ['GET'])
def runninglistvms():
	output = subprocess.check_output(['VBoxManage','list','runningvms'])
	return output

# Este metodo retorna las caracteristica de una maquina virtual cuyo nombre es
# vmname 3.
# como invocar: curl http://localhost:5000/vms/info/<nombreMaquina>
@app.route('/vms/info/<vmname>', methods = ['GET'])
def vminfo(vmname):	
	
	search = subprocess.Popen(['VBoxManage','list','vms'],stdout = subprocess.PIPE)
	filtro = subprocess.Popen(['grep', vmname],stdin = search.stdout, stdout = subprocess.PIPE)
	exist = subprocess.check_output(['wc','-l'],stdin = filtro.stdout)
	bol = int(exist)

	output = ""
	if bol == 1:
		grepCPU = subprocess.Popen(['VBoxManage','showvminfo',vmname],stdout = subprocess.PIPE)
		Cpus = subprocess.check_output(['grep','CPUs'],stdin = grepCPU.stdout)	
		grepRam = subprocess.Popen(['VBoxManage','showvminfo',vmname],stdout = subprocess.PIPE)
		Ram = subprocess.check_output(['grep','Memory size'],stdin = grepRam.stdout)
		grepInter = subprocess.Popen(['VBoxManage','showvminfo',vmname],stdout = subprocess.PIPE)
		inter = subprocess.check_output(['grep','NIC'],stdin = grepInter.stdout)

		output += Cpus + Ram + inter
	else:
		output += "No existe una maquina Virtual con el nombre: " + vmname + "\n"
	return output
	

# Este metodo permite crear una maquina virtual
#Como invocar: curl --data "Nombre=<nombre>&Disco=<valor>&Ram=<valor>&CPUS=<valor>" "http://localhost:5000/vms/create"
@app.route('/vms/create', methods = ['POST'])
def vmcreate():	
	nombre = request.form['Nombre']
	disco = request.form['Disco']
	ram = request.form['Ram']
	numCpus = request.form['CPUS']

	search = subprocess.Popen(['VBoxManage','list','vms'],stdout = subprocess.PIPE)
	filtro = subprocess.Popen(['grep', nombre],stdin = search.stdout, stdout = subprocess.PIPE)
	exist = subprocess.check_output(['wc','-l'],stdin = filtro.stdout)
	bol = int(exist)

	output = "Creando Maquina virtual....\n"

	if bol == 0:
		output += subprocess.check_output(['./scriptMaquina',nombre,disco,ram,numCpus])
		output += "\n Maquina virtual creada con exito\n"
	else:
		output += "Ya se ha creado una maquina virtual con el nombre: " + nombre + "\n"
	return output
	
	

# Este metodo permite eliminar una maquina virtual
#como invocar: curl -X DELETE http://localhost:5000/vms/delete
@app.route('/vms/delete/<name>', methods = ['DELETE'])
def vmDelete(name):
	search = subprocess.Popen(['VBoxManage','list','vms'],stdout = subprocess.PIPE)
	filtro = subprocess.Popen(['grep', name],stdin = search.stdout, stdout = subprocess.PIPE)
	exist = subprocess.check_output(['wc','-l'],stdin = filtro.stdout)
	bol = int(exist)

	output = "Eliminando maquina Virtual....\n"

	if bol == 1:
		output += subprocess.check_output(['VBoxManage','unregistervm',name,'--delete'])
		output += "\n Maquina virtual eliminada con exito\n"
	else:
		output += "No existe una maquina Virtual con el nombre: " + name + "\n"
	return output

if __name__ == '__main__':
        app.run(debug = True, host='0.0.0.0')
