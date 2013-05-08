#!/usr/bin/env python

__author__ = 'apprentice1989@gmail.com (Huang Shitao)'


from dataaccess import DataAccess
import numpy
import ahp


class DataProc:
	_level_tree = {}
	
	def __init__(self, raw):
		self._data_access = DataAccess(raw)


	def start():
        '''Start calculating...'''
		_build_level_tree()
		_set_value2level_tree()
		_calculate_and_set_weight2level_tree()
		weights = _fuzzy_synthetic_evaluation()
		result = _calculate_final_score(weights)
        return result


	def _build_level_tree():
		_level_data = self._data_access.get_level_data()
		for _each in _level_data:
			_level_node = {}
			_level_node["id"] = _each[0]
			_level_node["pid"] = _each[1]
			_level_node["eval"] = []
			_level_node["weight"] = 0.0
			_level_node["cid"] = []
			self._level_tree[_level_node["id"]] = _level_node

		_root_node = {}
		_root_node["id"] = -1
		_root_node["pid"] = None
		_root_node["eval"] = []
		_root_node["cid"] = []
		self._level_tree[_root_node["id"]] = _root_node

		for _item in self._level_tree:
			if self._level_tree[_item]["pid"] is not None:
				self._level_tree[self._level_tree[_item]["pid"]]["cid"].append(_item)


	def _set_value2level_tree():
		#Get the experts' evaluations.
		_evals = self._data_access.get_evals()
		_classes = self._data_access.get_classes()
		_count = {}
		_fids = set()

		for _eval in _evals:
			_fids.add(_eval[0])

		#Initialize
		for _fid in _fids:
			_count[_fid] = {}
			_count[_fid]['total'] = 0
			for _class in _classes:
				_count[_fid][_class[0]] = 0

		#calculate the evaluation
		for _each in _evals:
			_count[_each[0]][_each[1]] += 1
			_count[_each[0]]["total"] += 1

		#Set the evaluations to the level tree
		for _item in _count:
			for _cla in _classes:
				self._level_tree[_item]["eval"].append(float(_count[_item][_cla[0]]) / float(_count[_item]["total"]))


	def _fuzzy_synthetic_evaluation():
		return _AoR(self._level_tree[-1])


	def _AoR(root_node={}):
		if root_node["cid"]:
			_A = []
			_R = []
			for _cid in root_node["cid"]:
				_A.append(self._level_tree[_cid]["weight"])
				_r = _AoR(self._level_tree[_cid])
				_R.append(_r)
			root_node["eval"] = numpy.dot(_A, _R)
		return root_node["eval"]


	def _calculate_and_set_weight2level_tree():
		_weight_result = self._data_access.get_weight_result()
		_fids = get_fids()
		_result, _new_weight_result = _build_new_result(_weight_result, _fids)
		_matrixs = _build_matrixs(_result, _fids, _new_weight_result)
	
		for _item in _matrixs:
			weight, eigenvalues, eigenvector = ahp.calculate_weight(_matrixs[_item])
			_fids[_item]["result"] = weight

		for _each in _fids:
			for _cid in self._level_tree[_each]["cid"]:
				self._level_tree[_cid]["weight"] = _fids[_each]["result"][_new_weight_result[_cid]]
	

	def _get_fids():
		'''Get all parents' id.'''
		fids = {}
		for _id in self._level_tree:
			if self._level_tree[_id]["cid"]:
				fids[_id] = {}
				fids[_id]["count"] = 0
				fids[_id]["result"] = []
		return fids
	

	def _build_matrixs(result={}, fids={}, new_weight_result={}):
		matrixs = {}
		for _each in result:
			matrixs[_each] = numpy.ones(shape=(fids[_each]["count"], fids[_each]["count"]))
			for _item in result[_each]:
				matrixs[_each][_item[0]][_item[1]] = float(_item[2])
		return matrixs


	def _build_new_result(weight_result=[], fids={}):
		result = {}
		#Store the sub index
		new_weight_result = {}
		for _each in weight_result:
			if self._level_tree[_each[0]]["pid"] in fids:
				if _each[0] not in new_weight_result:
					__x = fids[self._level_tree[_each[0]]["pid"]]["count"]
					new_weight_result[_each[0]] = __x
					fids[self._level_tree[_each[0]]["pid"]]["count"] += 1
				else:
					__x = new_weight_result[_each[0]]

				if _each[1] not in new_weight_result:
					__y = fids[self._level_tree[_each[1]]["pid"]]["count"]
					new_weight_result[_each[1]] = __y
					fids[self._level_tree[_each[1]]["pid"]]["count"] += 1
				else:
					__y = new_weight_result[_each[1]]
	
				if self._level_tree[_each[0]]["pid"] in result:
					result[self._level_tree[_each[0]]["pid"]].append([__x, __y, _each[2]])
				else:
					result[self._level_tree[_each[0]]["pid"]] = []
					result[self._level_tree[_each[0]]["pid"]].append([__x, __y, _each[2]])
		return result, new_weight_result


	def _calculate_final_score(weights=[]):
		return numpy.dot(weights, [each[1] for each in self._data_access.get_classes()])
