



class hr_multa(Model):
    _name = "hr.multa"
    _columns = {
        'name':fields.char("Name", required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'date': fields.date("Date", required=True),
        'total': fields.float("Valor de la Multa", required=True),
        'state': fields.selection([
                ('pending', "Pending"),
                ('paid', "Paid")], "State", required=True, default='pending')
    }
